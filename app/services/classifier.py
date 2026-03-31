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

        Rules:
        - expense: TRANSACTION_AMOUNT < 0
        - income: TRANSACTION_AMOUNT > 0
        - transfer: TRANSACTION_TYPE contains "transfer" or DESCRIPTION contains "transferencia"
        - refund: TRANSACTION_TYPE = "refund"
        - ignored: ajustes internos y fees técnicos

        Returns:
            (TransactionType, confidence: float 0-1)
        """
        desc_lower = description.lower() if description else ""

        # Rule 1: Check for ignored patterns (highest priority)
        if any(kw in desc_lower for kw in self.IGNORED_KEYWORDS):
            return (TransactionType.ADJUSTMENT, 0.95)

        # Rule 2: Check TRANSACTION_TYPE for refund (high priority)
        if transaction_type_raw and transaction_type_raw.lower().strip() == 'refund':
            return (TransactionType.REFUND, 0.95)

        # Rule 3: Check for transfer patterns in TRANSACTION_TYPE or DESCRIPTION
        if transaction_type_raw and 'transfer' in transaction_type_raw.lower():
            return (TransactionType.TRANSFER, 0.90)

        if 'transferencia' in desc_lower:
            return (TransactionType.TRANSFER, 0.90)

        # Also check other transfer keywords for robustness
        if any(kw in desc_lower for kw in self.TRANSFER_KEYWORDS):
            return (TransactionType.TRANSFER, 0.85)

        # Rule 4: Amount-based classification (primary rule)
        if amount < 0:
            # Negative amount = expense
            return (TransactionType.EXPENSE, 0.85)
        elif amount > 0:
            # Positive amount = income
            return (TransactionType.INCOME, 0.85)
        else:
            # Amount is exactly 0 - check other signals
            # Check for adjustment patterns
            if any(kw in desc_lower for kw in self.ADJUSTMENT_KEYWORDS):
                return (TransactionType.ADJUSTMENT, 0.80)

            # Fallback to uncategorized
            return (TransactionType.EXPENSE, 0.30)

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
