"""
Robust import service for MercadoPago CSV/Excel files
Handles all columns, classification, categorization, and normalization
"""
import hashlib
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional
import pandas as pd
import re

from app.models.enums import TransactionType, SourceType, TransactionStatus, TransactionNature, Currency
from app.models.transaction import (
    TransactionCreate,
    TransactionImportBatch,
    TransactionImportBatchCreate,
    RawImportRow,
    RawImportRowCreate,
)
from app.repositories import get_db
from app.services.classifier import TransactionClassifier
from app.services.categorizer import TransactionCategorizer
from app.services.merchant_normalizer import MerchantNormalizer
from config.settings import DEDUPLICATION_WINDOW_DAYS, DEDUPLICATION_TOLERANCE_AMOUNT


class MercadoPagoImporter:
    """
    Robust importer for MercadoPago exports with full column support
    """

    # Primary columns mapping (MercadoPago → internal)
    PRIMARY_COLUMNS = {
        'SOURCE_ID': 'external_id',
        'EXTERNAL_REFERENCE': 'source_reference',
        'ORDER_ID': 'order_id',
        'TRANSACTION_DATE': 'operation_date',
        'SETTLEMENT_DATE': 'settlement_date',
        'MONEY_RELEASE_DATE': 'available_date',
        'TRANSACTION_AMOUNT': 'gross_amount',
        'REAL_AMOUNT': 'real_amount',
        'SETTLEMENT_NET_AMOUNT': 'net_amount',
        'FEE_AMOUNT': 'fee_amount',
        'TRANSACTION_CURRENCY': 'transaction_currency',
        'SETTLEMENT_CURRENCY': 'settlement_currency',
        'TRANSACTION_TYPE': 'transaction_type_raw',
        'DESCRIPTION': 'description_raw',
        'PAYMENT_METHOD': 'payment_method',
        'PAYMENT_METHOD_TYPE': 'payment_method_type',
        'OPERATION_TAGS': 'operation_tags',
        'INSTALLMENTS': 'installments',
        'STORE_NAME': 'store_name',
        'POS_NAME': 'pos_name',
        'PAYER_NAME': 'counterparty_name',
        'POI_WALLET_NAME': 'wallet_name',
        'POI_BANK_NAME': 'bank_name',
        'CARD_INITIAL_NUMBER': 'card_last_digits',
        'METADATA': 'metadata',
    }

    # Secondary columns (saved only to raw_metadata)
    SECONDARY_COLUMNS = [
        'USER_ID', 'PACK_ID', 'SHIPPING_ID', 'POS_ID', 'STORE_ID',
        'EXTERNAL_POS_ID', 'EXTERNAL_STORE_ID', 'PAYER_ID_TYPE',
        'PAYER_ID_NUMBER', 'POI_ID', 'BUSINESS_UNIT', 'SUB_UNIT',
        'TAX_DETAIL', 'TAXES_DISAGGREGATED', 'SHIPMENT_MODE', 'SITE',
        'MKP_FEE_AMOUNT', 'FINANCING_FEE_AMOUNT', 'SHIPPING_FEE_AMOUNT',
        'TAXES_AMOUNT', 'TAX_AMOUNT_TELCO', 'FEE_PREVISION',
        'COUPON_AMOUNT', 'SELLER_AMOUNT'
    ]

    def __init__(self):
        self.db = get_db()
        self.classifier = TransactionClassifier()
        self.categorizer = TransactionCategorizer()
        self.merchant_normalizer = MerchantNormalizer()

    def import_file(
        self,
        file_path: Path,
        source_type: SourceType,
        account_id: Optional[str] = None,
        credit_card_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Import MercadoPago file with full processing

        Returns:
            Import batch result dict
        """
        # Create import batch
        batch_id = f"batch_{uuid.uuid4().hex[:12]}"
        batch = TransactionImportBatchCreate(
            source_type=source_type,
            filename=file_path.name,
            total_rows=0,
        )

        self.db.add('transaction_import_batches', batch_id, batch)

        try:
            # Parse file
            df = self._parse_file(file_path)

            # Update total rows
            total_rows = len(df)
            self.db.update('transaction_import_batches', batch_id, {
                'total_rows': total_rows
            })

            # Process each row
            processed = 0
            failed = 0
            duplicated = 0
            review_required = 0

            for idx, row in df.iterrows():
                try:
                    # Save raw import row
                    raw_row_id = f"raw_{batch_id}_{idx}"
                    raw_row = RawImportRowCreate(
                        import_batch_id=batch_id,
                        row_number=int(idx),
                        raw_data=row.to_dict(),
                        parsed_successfully=False,
                    )
                    self.db.add('raw_import_rows', raw_row_id, raw_row)

                    # Parse row to transaction
                    tx_data, status, confidence = self._parse_row(
                        row,
                        source_type,
                        account_id,
                        credit_card_id,
                        batch_id,
                        raw_row_id,
                    )

                    # Check for duplicates
                    if self._is_duplicate(tx_data):
                        duplicated += 1
                        tx_data['status'] = TransactionStatus.DUPLICATED
                    else:
                        tx_data['status'] = status

                    # Check if needs review
                    if confidence < 0.6 and status == TransactionStatus.CONFIRMED:
                        tx_data['status'] = TransactionStatus.PENDING
                        tx_data['tags'].append('necesita_revision')
                        review_required += 1

                    # Save transaction
                    tx_id = f"tx_{uuid.uuid4().hex[:12]}"
                    transaction = TransactionCreate(**tx_data)
                    self.db.add('transactions', tx_id, transaction)

                    # Update raw row with success
                    self.db.update('raw_import_rows', raw_row_id, {
                        'parsed_successfully': True,
                        'created_transaction_id': tx_id,
                    })

                    processed += 1

                except Exception as e:
                    failed += 1
                    # Update raw row with error
                    self.db.update('raw_import_rows', raw_row_id, {
                        'parsed_successfully': False,
                        'error_message': str(e),
                    })

            # Update batch with final results
            self.db.update('transaction_import_batches', batch_id, {
                'processed_rows': processed,
                'failed_rows': failed,
                'duplicated_rows': duplicated,
                'status': 'completado',
                'completed_at': datetime.now().isoformat(),
                'metadata': {
                    'review_required': review_required
                }
            })

            return self.db.get('transaction_import_batches', batch_id)

        except Exception as e:
            # Update batch with error
            self.db.update('transaction_import_batches', batch_id, {
                'status': 'fallido',
                'error_message': str(e),
                'completed_at': datetime.now().isoformat(),
            })
            raise

    def _parse_file(self, file_path: Path) -> pd.DataFrame:
        """Parse CSV or Excel file"""
        # Detect file type and read
        if file_path.suffix.lower() in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        else:
            # Try different encodings for CSV
            for encoding in ['utf-8', 'latin-1', 'iso-8859-1']:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except (UnicodeDecodeError, Exception):
                    continue
            else:
                raise ValueError("No se pudo decodificar el archivo CSV")

        # Normalize column names (uppercase, strip whitespace)
        df.columns = df.columns.str.strip().str.upper()

        return df

    def _parse_row(
        self,
        row: pd.Series,
        source_type: SourceType,
        account_id: Optional[str],
        credit_card_id: Optional[str],
        batch_id: str,
        raw_row_id: str,
    ) -> tuple[Dict[str, Any], TransactionStatus, float]:
        """
        Parse a row into transaction data with classification

        Returns:
            (tx_data, status, confidence)
        """
        # Extract primary fields
        primary_data = self._extract_primary_fields(row)

        # Extract amount (can be negative)
        raw_amount = primary_data.get('gross_amount', 0)
        abs_amount = abs(raw_amount) if raw_amount else 0

        # Extract description
        description_raw = primary_data.get('description_raw') or 'Sin descripción'
        description = str(description_raw).strip()

        # Extract and normalize merchant
        merchant_raw = self._extract_merchant_raw(row, description)
        merchant_normalized = self.merchant_normalizer.normalize(merchant_raw) if merchant_raw else None
        merchant_display = merchant_normalized or merchant_raw

        # Classify transaction type
        tx_type, classification_confidence = self.classifier.classify(
            amount=raw_amount,
            description=description,
            transaction_type_raw=primary_data.get('transaction_type_raw'),
            payment_method=primary_data.get('payment_method'),
            payment_method_type=primary_data.get('payment_method_type'),
            operation_tags=primary_data.get('operation_tags'),
            store_name=primary_data.get('store_name'),
            pos_name=primary_data.get('pos_name'),
        )

        # Categorize transaction
        category, category_confidence, category_reason = self.categorizer.categorize(
            merchant_normalized=merchant_normalized,
            description=description,
            payment_method=primary_data.get('payment_method'),
            transaction_type_str=tx_type.value,
        )

        # Classify nature
        nature = self.classifier.classify_nature(
            transaction_type=tx_type,
            merchant_normalized=merchant_normalized,
            category=category,
            installments=primary_data.get('installments'),
        )

        # Parse dates
        operation_date = self._parse_date(primary_data.get('operation_date'))
        settlement_date = self._parse_date(primary_data.get('settlement_date'))
        available_date = self._parse_date(primary_data.get('available_date'))

        # Generate deduplication key
        dedup_key = self._generate_deduplication_key(
            external_id=primary_data.get('external_id'),
            source_reference=primary_data.get('source_reference'),
            operation_date=operation_date,
            amount=abs_amount,
            description=description,
        )

        # Determine currency
        currency_code = primary_data.get('transaction_currency') or 'ARS'
        currency = Currency.ARS  # Default
        if currency_code == 'USD':
            currency = Currency.USD
        elif currency_code == 'EUR':
            currency = Currency.EUR

        # Build raw metadata (secondary columns)
        raw_metadata = self._extract_raw_metadata(row)

        # Determine status based on confidence
        if classification_confidence < 0.5:
            status = TransactionStatus.PENDING
        else:
            status = TransactionStatus.CONFIRMED

        # Build transaction data
        tx_data = {
            # Core
            'transaction_type': tx_type,
            'amount': abs_amount,
            'currency': currency,

            # Dates
            'operation_date': operation_date,
            'posting_date': operation_date,  # Same as operation for MP
            'settlement_date': settlement_date,
            'available_date': available_date,

            # Amounts
            'gross_amount': abs(primary_data.get('gross_amount', 0)) if primary_data.get('gross_amount') else None,
            'real_amount': abs(primary_data.get('real_amount', 0)) if primary_data.get('real_amount') else None,
            'net_amount': abs(primary_data.get('net_amount', 0)) if primary_data.get('net_amount') else None,
            'fee_amount': abs(primary_data.get('fee_amount', 0)) if primary_data.get('fee_amount') else None,

            # Merchant
            'merchant_raw': merchant_raw,
            'merchant_normalized': merchant_normalized,
            'merchant': merchant_display,

            # Description
            'description': description,
            'description_raw': description_raw,

            # Payment
            'payment_method': primary_data.get('payment_method'),
            'payment_method_type': primary_data.get('payment_method_type'),
            'installments': int(primary_data.get('installments')) if primary_data.get('installments') else None,
            'card_last_digits': self._extract_card_digits(primary_data.get('card_last_digits')),

            # Counterparty
            'counterparty_name': primary_data.get('counterparty_name'),
            'bank_name': primary_data.get('bank_name'),
            'wallet_name': primary_data.get('wallet_name'),

            # External IDs
            'external_id': primary_data.get('external_id'),
            'source_reference': primary_data.get('source_reference'),
            'order_id': primary_data.get('order_id'),

            # Categorization
            'category_id': None,  # User will assign final category
            'suggested_category_id': category,
            'category_confidence': category_confidence,
            'categorization_reason': category_reason,
            'nature': nature,
            'is_fixed_expense': nature == TransactionNature.FIXED,

            # Account linking
            'account_id': account_id,
            'credit_card_id': credit_card_id,

            # Import metadata
            'source_type': source_type,
            'import_batch_id': batch_id,
            'raw_import_row_id': raw_row_id,
            'deduplication_key': dedup_key,

            # Tags and metadata
            'tags': ['importado', 'mercadopago', category],
            'raw_metadata': raw_metadata,
        }

        return tx_data, status, min(classification_confidence, category_confidence)

    def _extract_primary_fields(self, row: pd.Series) -> Dict[str, Any]:
        """Extract primary columns from row"""
        data = {}
        for col_name, field_name in self.PRIMARY_COLUMNS.items():
            if col_name in row.index:
                value = row[col_name]
                # Convert NaN/None to None
                if pd.isna(value):
                    data[field_name] = None
                else:
                    data[field_name] = value
        return data

    def _extract_raw_metadata(self, row: pd.Series) -> Dict[str, Any]:
        """Extract secondary columns to raw metadata"""
        metadata = {}
        for col in row.index:
            if col.upper() in self.SECONDARY_COLUMNS:
                value = row[col]
                if not pd.isna(value):
                    metadata[col] = value
        return metadata

    def _extract_merchant_raw(self, row: pd.Series, description: str) -> Optional[str]:
        """Extract raw merchant name using priority order"""
        # Priority 1: STORE_NAME
        if 'STORE_NAME' in row.index and not pd.isna(row['STORE_NAME']):
            return str(row['STORE_NAME']).strip()

        # Priority 2: POS_NAME
        if 'POS_NAME' in row.index and not pd.isna(row['POS_NAME']):
            return str(row['POS_NAME']).strip()

        # Priority 3: Extract from DESCRIPTION
        if description:
            return self.merchant_normalizer.extract_from_description(description)

        return None

    def _extract_card_digits(self, card_initial: Any) -> Optional[str]:
        """Extract card last digits from CARD_INITIAL_NUMBER"""
        if pd.isna(card_initial):
            return None

        card_str = str(card_initial).strip()
        # Extract last 4 digits if present
        digits = re.findall(r'\d+', card_str)
        if digits:
            last_digits = digits[-1][-4:] if len(digits[-1]) >= 4 else digits[-1]
            return f"****{last_digits}"

        return None

    def _parse_date(self, date_value: Any) -> Optional[datetime]:
        """Parse date value to datetime"""
        if pd.isna(date_value):
            return None

        try:
            if isinstance(date_value, datetime):
                return date_value
            return pd.to_datetime(date_value)
        except:
            return None

    def _generate_deduplication_key(
        self,
        external_id: Optional[str],
        source_reference: Optional[str],
        operation_date: Optional[datetime],
        amount: float,
        description: str,
    ) -> str:
        """Generate robust deduplication key"""
        # Prefer external IDs if available
        if external_id:
            key_str = f"mp_source_{external_id}"
        elif source_reference:
            key_str = f"mp_ref_{source_reference}"
        else:
            # Fallback: date + amount + description
            date_str = operation_date.strftime('%Y%m%d') if operation_date else 'nodate'
            desc_clean = re.sub(r'\W+', '', description.lower())[:30]
            key_str = f"mp_{date_str}_{amount:.2f}_{desc_clean}"

        return hashlib.sha256(key_str.encode()).hexdigest()[:16]

    def _is_duplicate(self, tx_data: Dict[str, Any]) -> bool:
        """Check if transaction is duplicate"""
        dedup_key = tx_data.get('deduplication_key')
        if not dedup_key:
            return False

        operation_date = tx_data.get('operation_date')
        if not operation_date:
            return False

        # Search window
        window_start = operation_date - timedelta(days=DEDUPLICATION_WINDOW_DAYS)
        window_end = operation_date + timedelta(days=DEDUPLICATION_WINDOW_DAYS)

        # Query existing transactions
        all_transactions = self.db.get_all('transactions')

        for tx in all_transactions:
            if tx.get('deduplication_key') == dedup_key:
                tx_date_str = tx.get('operation_date')
                if tx_date_str:
                    tx_date = datetime.fromisoformat(tx_date_str) if isinstance(tx_date_str, str) else tx_date_str
                    if window_start <= tx_date <= window_end:
                        # Check amount tolerance
                        amount_diff = abs(tx.get('amount', 0) - tx_data.get('amount', 0))
                        if amount_diff <= DEDUPLICATION_TOLERANCE_AMOUNT:
                            return True

        return False
