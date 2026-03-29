"""
Transaction models including import batches and raw data
"""
from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, ConfigDict
from .enums import (
    TransactionType,
    TransactionNature,
    TransactionStatus,
    SourceType,
    Currency
)


class TransactionBase(BaseModel):
    """Base transaction schema"""
    # Core transaction data
    transaction_type: TransactionType = Field(..., description="Type of transaction")
    amount: float = Field(..., gt=0, description="Transaction amount (always positive)")
    currency: Currency = Field(default=Currency.ARS, description="Transaction currency")

    # Dates
    operation_date: datetime = Field(..., description="Date when transaction occurred")
    posting_date: Optional[datetime] = Field(None, description="Date when transaction posted")
    settlement_date: Optional[datetime] = Field(None, description="Settlement date")
    available_date: Optional[datetime] = Field(None, description="Money available date")

    # Amounts (MercadoPago extended fields)
    gross_amount: Optional[float] = Field(None, description="Gross amount (TRANSACTION_AMOUNT)")
    real_amount: Optional[float] = Field(None, description="Real amount after fees")
    net_amount: Optional[float] = Field(None, description="Net settlement amount")
    fee_amount: Optional[float] = Field(None, description="Total fees")

    # Descriptions and metadata
    merchant_raw: Optional[str] = Field(None, description="Raw merchant name from source")
    merchant_normalized: Optional[str] = Field(None, description="Normalized merchant name")
    merchant: Optional[str] = Field(None, description="Final merchant display name")
    description: str = Field(..., min_length=1, description="Transaction description")
    description_raw: Optional[str] = Field(None, description="Raw description from source")
    notes: Optional[str] = Field(None, description="User notes")

    # Payment details
    payment_method: Optional[str] = Field(None, description="Payment method (e.g., credit_card)")
    payment_method_type: Optional[str] = Field(None, description="Payment method type")
    installments: Optional[int] = Field(None, description="Number of installments")
    card_last_digits: Optional[str] = Field(None, description="Card last 4 digits or mask")

    # Counterparty info
    counterparty_name: Optional[str] = Field(None, description="Payer/payee name")
    bank_name: Optional[str] = Field(None, description="Bank name if applicable")
    wallet_name: Optional[str] = Field(None, description="Wallet name (e.g., POI)")

    # External references
    external_id: Optional[str] = Field(None, description="External ID from source (SOURCE_ID)")
    source_reference: Optional[str] = Field(None, description="Source reference (EXTERNAL_REFERENCE)")
    order_id: Optional[str] = Field(None, description="Order ID if applicable")

    # Categorization
    category_id: Optional[str] = Field(None, description="Category ID")
    suggested_category_id: Optional[str] = Field(None, description="Auto-suggested category ID")
    category_confidence: Optional[float] = Field(None, ge=0, le=1, description="Category confidence 0-1")
    categorization_reason: Optional[str] = Field(None, description="Reason for categorization")
    nature: Optional[TransactionNature] = Field(None, description="Transaction nature")
    is_fixed_expense: bool = Field(default=False, description="Whether it's a fixed expense")

    # Account linking
    account_id: Optional[str] = Field(None, description="Source account ID")
    credit_card_id: Optional[str] = Field(None, description="Source credit card ID")

    # Transfer linking (if transaction_type == TRANSFER)
    transfer_destination_account_id: Optional[str] = Field(
        None,
        description="Destination account for transfers"
    )

    # Import metadata
    source_type: SourceType = Field(default=SourceType.MANUAL, description="Source of transaction")
    import_batch_id: Optional[str] = Field(None, description="Import batch ID")
    raw_import_row_id: Optional[str] = Field(None, description="Raw import row ID for traceability")

    # Deduplication and status
    deduplication_key: Optional[str] = Field(None, description="Key for detecting duplicates")
    status: TransactionStatus = Field(
        default=TransactionStatus.CONFIRMED,
        description="Transaction status"
    )

    # Tags and raw metadata
    tags: List[str] = Field(default_factory=list, description="User-defined tags")
    raw_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Raw imported data for traceability"
    )


class TransactionCreate(TransactionBase):
    """Schema for creating transaction"""
    pass


class Transaction(TransactionBase):
    """Complete transaction model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique transaction ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class TransactionImportBatchBase(BaseModel):
    """Base import batch schema"""
    source_type: SourceType = Field(..., description="Source type of import")
    filename: Optional[str] = Field(None, description="Original filename")
    total_rows: int = Field(..., ge=0, description="Total rows in import")
    processed_rows: int = Field(default=0, ge=0, description="Successfully processed rows")
    failed_rows: int = Field(default=0, ge=0, description="Failed rows")
    duplicated_rows: int = Field(default=0, ge=0, description="Duplicated rows detected")
    status: str = Field(default="procesando", description="Import status")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class TransactionImportBatchCreate(TransactionImportBatchBase):
    """Schema for creating import batch"""
    pass


class TransactionImportBatch(TransactionImportBatchBase):
    """Complete import batch model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique batch ID")
    created_at: datetime = Field(default_factory=datetime.now)
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")


class RawImportRowBase(BaseModel):
    """Base raw import row schema - stores original imported data"""
    import_batch_id: str = Field(..., description="Parent batch ID")
    row_number: int = Field(..., ge=0, description="Row number in import file")
    raw_data: Dict[str, Any] = Field(..., description="Complete raw row data as dict")
    parsed_successfully: bool = Field(default=False, description="Whether parsing succeeded")
    error_message: Optional[str] = Field(None, description="Parse error if any")
    created_transaction_id: Optional[str] = Field(
        None,
        description="Transaction ID created from this row"
    )


class RawImportRowCreate(RawImportRowBase):
    """Schema for creating raw import row"""
    pass


class RawImportRow(RawImportRowBase):
    """Complete raw import row model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique raw row ID")
    created_at: datetime = Field(default_factory=datetime.now)
