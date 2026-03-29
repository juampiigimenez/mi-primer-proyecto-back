"""
Transaction classifier - Determines transaction type based on multiple signals
"""
import re
from typing import Dict, Any, Tuple
from app.models.enums import TransactionType, TransactionNature


class TransactionClassifier:
    """
    Robust transaction classifier for MercadoPago data
    Uses multiple signals to determine transaction type and nature
    """

    # Keywords for classification
    EXPENSE_KEYWORDS = [
        'payment', 'purchase', 'pago', 'compra', 'qr', 'point', 'pos',
        'debit', 'débito', 'cargo', 'consumo', 'comercio', 'tienda',
        'store', 'shop', 'merchant', 'venta'
    ]

    INCOME_KEYWORDS = [
        'transferencia recibida', 'cobro', 'received', 'collection',
        'payout', 'ingreso', 'acreditación', 'acreditacion', 'deposito',
        'depósito', 'venta', 'income', 'credit'
    ]

    TRANSFER_KEYWORDS = [
        'transferencia', 'transfer', 'retiro', 'extracción', 'extraccion',
        'bank transfer', 'cash out', 'add money', 'top up', 'carga',
        'recarga', 'envio', 'envío', 'sent', 'withdrawal'
    ]

    REFUND_KEYWORDS = [
        'refund', 'devolución', 'devolucion', 'reversal', 'reintegro',
        'contracargo', 'cancelación', 'cancelacion', 'anulación', 'anulacion'
    ]

    ADJUSTMENT_KEYWORDS = [
        'fee reversal', 'ajuste', 'correction', 'balance adjustment',
        'corrección', 'correccion', 'technical'
    ]

    IGNORED_KEYWORDS = [
        'impuesto interno', 'tax detail', 'fee breakdown', 'comisión desglosada',
        'comision desglosada'
    ]

    # Transaction type patterns (MercadoPago specific)
    MP_TYPE_MAPPING = {
        'payment': TransactionType.EXPENSE,
        'money_transfer': TransactionType.TRANSFER,
        'refund': TransactionType.REFUND,
        'chargeback': TransactionType.REFUND,
        'payout': TransactionType.INCOME,
        'topup': TransactionType.TRANSFER,
        'withdrawal': TransactionType.TRANSFER,
    }

    def classify(
        self,
        amount: float,
        description: str,
        transaction_type_raw: str = None,
        payment_method: str = None,
        payment_method_type: str = None,
        operation_tags: str = None,
        store_name: str = None,
        pos_name: str = None,
    ) -> Tuple[TransactionType, float]:
        """
        Classify transaction type with confidence score

        Returns:
            (TransactionType, confidence: float 0-1)
        """
        signals = []
        confidence = 0.0

        # Signal 1: MercadoPago transaction_type (high confidence)
        if transaction_type_raw:
            tx_type_lower = transaction_type_raw.lower().strip()
            if tx_type_lower in self.MP_TYPE_MAPPING:
                signals.append(('mp_type', self.MP_TYPE_MAPPING[tx_type_lower], 0.9))

        # Signal 2: Amount sign (medium confidence)
        if amount < 0:
            signals.append(('amount_negative', TransactionType.EXPENSE, 0.6))
        elif amount > 0:
            signals.append(('amount_positive', TransactionType.INCOME, 0.5))

        # Signal 3: Description keywords (high confidence for specific patterns)
        desc_lower = description.lower() if description else ""

        # Check for ignored patterns
        if any(kw in desc_lower for kw in self.IGNORED_KEYWORDS):
            return (TransactionType.ADJUSTMENT, 0.95)  # Mark as ignored/adjustment

        # Check refund patterns (high priority)
        if any(kw in desc_lower for kw in self.REFUND_KEYWORDS):
            signals.append(('desc_refund', TransactionType.REFUND, 0.85))

        # Check transfer patterns
        if any(kw in desc_lower for kw in self.TRANSFER_KEYWORDS):
            signals.append(('desc_transfer', TransactionType.TRANSFER, 0.8))

        # Check adjustment patterns
        if any(kw in desc_lower for kw in self.ADJUSTMENT_KEYWORDS):
            signals.append(('desc_adjustment', TransactionType.ADJUSTMENT, 0.8))

        # Check expense patterns
        if any(kw in desc_lower for kw in self.EXPENSE_KEYWORDS):
            signals.append(('desc_expense', TransactionType.EXPENSE, 0.75))

        # Check income patterns
        if any(kw in desc_lower for kw in self.INCOME_KEYWORDS):
            signals.append(('desc_income', TransactionType.INCOME, 0.75))

        # Signal 4: Store/POS presence (strong indicator of expense)
        if store_name or pos_name:
            signals.append(('has_store', TransactionType.EXPENSE, 0.8))

        # Signal 5: Payment method type
        if payment_method_type:
            pm_type_lower = payment_method_type.lower()
            if pm_type_lower in ['debit_card', 'credit_card', 'prepaid_card']:
                signals.append(('pm_card', TransactionType.EXPENSE, 0.7))
            elif pm_type_lower in ['account_money', 'digital_wallet']:
                # Could be either, rely on other signals
                pass

        # Signal 6: Payment method
        if payment_method:
            pm_lower = payment_method.lower()
            if 'transfer' in pm_lower:
                signals.append(('pm_transfer', TransactionType.TRANSFER, 0.75))

        # Aggregate signals using weighted voting
        if not signals:
            # No signals, use amount sign as fallback
            if amount < 0:
                return (TransactionType.EXPENSE, 0.3)
            else:
                return (TransactionType.INCOME, 0.3)

        # Count votes per type with weights
        votes: Dict[TransactionType, float] = {}
        for signal_name, tx_type, weight in signals:
            votes[tx_type] = votes.get(tx_type, 0) + weight

        # Get winner
        winner_type = max(votes, key=votes.get)
        max_vote = votes[winner_type]
        total_votes = sum(votes.values())

        # Calculate confidence (normalized)
        confidence = min(max_vote / total_votes, 1.0) if total_votes > 0 else 0.5

        return (winner_type, confidence)

    def classify_nature(
        self,
        transaction_type: TransactionType,
        merchant_normalized: str = None,
        category: str = None,
        installments: int = None,
    ) -> TransactionNature:
        """
        Classify transaction nature (fixed, variable, etc.)

        Args:
            transaction_type: Already classified transaction type
            merchant_normalized: Normalized merchant name
            category: Suggested category
            installments: Number of installments

        Returns:
            TransactionNature
        """
        # Income types
        if transaction_type == TransactionType.INCOME:
            if category == 'salary':
                return TransactionNature.INCOME_SALARY
            elif category in ['freelance', 'work']:
                return TransactionNature.INCOME_FREELANCE
            else:
                return TransactionNature.INCOME_OTHER

        # Transfer/savings
        if transaction_type == TransactionType.TRANSFER:
            if merchant_normalized and any(kw in merchant_normalized for kw in ['ahorro', 'savings', 'investment']):
                return TransactionNature.SAVINGS
            return TransactionNature.INVESTMENT  # Default for transfers

        # Expenses - check if fixed or variable
        if transaction_type == TransactionType.EXPENSE:
            # Fixed expenses (recurring services)
            fixed_categories = [
                'rent', 'utilities', 'subscriptions', 'insurance',
                'alquiler', 'servicios', 'suscripciones'
            ]
            if category and any(cat in category for cat in fixed_categories):
                return TransactionNature.FIXED

            # Debt payment
            if category in ['credit_card_payment', 'loan_payment']:
                return TransactionNature.DEBT_PAYMENT

            # Variable expenses (default for most purchases)
            return TransactionNature.VARIABLE

        # Default
        return TransactionNature.VARIABLE
