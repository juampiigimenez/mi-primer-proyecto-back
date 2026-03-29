"""
Import service for parsing CSV/Excel files from various sources
Redirects to robust MercadoPago importer
"""
from pathlib import Path
from typing import Dict, Any, Optional

from app.models.enums import SourceType
from app.services.importer_robust import MercadoPagoImporter
from app.repositories import get_db


class ImportService:
    """
    Service for importing transactions from files
    Delegates to specialized importers based on source type
    """

    def __init__(self):
        self.db = get_db()
        self.mp_importer = MercadoPagoImporter()

    def import_file(
        self,
        file_path: Path,
        source_type: SourceType,
        account_id: Optional[str] = None,
        credit_card_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Import transactions from file

        Args:
            file_path: Path to CSV/Excel file
            source_type: Source type (mercadopago_csv, mercadopago_excel, etc)
            account_id: Optional default account ID
            credit_card_id: Optional default credit card ID

        Returns:
            Import batch result dict
        """
        # Delegate to appropriate importer
        if source_type in [SourceType.MERCADOPAGO_CSV, SourceType.MERCADOPAGO_EXCEL]:
            return self.mp_importer.import_file(
                file_path=file_path,
                source_type=source_type,
                account_id=account_id,
                credit_card_id=credit_card_id,
            )
        else:
            raise ValueError(f"Unsupported source type: {source_type}")

    def get_batch_status(self, batch_id: str) -> Optional[Dict[str, Any]]:
        """Get import batch status"""
        return self.db.get('transaction_import_batches', batch_id)

    def get_all_batches(self) -> list[Dict[str, Any]]:
        """Get all import batches"""
        return self.db.get_all('transaction_import_batches')

    def get_batch_transactions(self, batch_id: str) -> list[Dict[str, Any]]:
        """Get all transactions from a batch"""
        return self.db.query(
            'transactions',
            lambda tx: tx.get('import_batch_id') == batch_id
        )

    def get_batch_raw_rows(self, batch_id: str) -> list[Dict[str, Any]]:
        """Get all raw import rows from a batch"""
        return self.db.query(
            'raw_import_rows',
            lambda row: row.get('import_batch_id') == batch_id
        )
