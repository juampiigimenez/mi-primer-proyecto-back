"""
Import History model - Track confirmed import batches
"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Literal


class ImportHistory(BaseModel):
    """Record of a confirmed import batch"""

    id: str = Field(..., description="Unique identifier (e.g., hist-abc123)")
    filename: str = Field(..., description="Original filename (e.g., settlement-x-2024-04-18.csv)")
    uploaded_at: datetime = Field(..., description="When the file was uploaded")
    confirmed_at: datetime = Field(..., description="When the import was confirmed")
    batch_id: str = Field(..., description="Reference to the import batch")
    status: Literal["confirmed"] = Field(default="confirmed", description="Import status")
    total_transactions: int = Field(..., ge=0, description="Total number of transactions")
    total_ingresos: float = Field(..., ge=0, description="Total income amount")
    total_gastos: float = Field(..., ge=0, description="Total expense amount")
    week_number: int = Field(..., ge=1, le=53, description="ISO 8601 week number")
    display_name: str = Field(..., description="Display name (e.g., Semana 16 - 2024)")

    class Config:
        json_schema_extra = {
            "example": {
                "id": "hist-abc123",
                "filename": "settlement-x-2024-04-18.csv",
                "uploaded_at": "2024-04-18T14:25:00",
                "confirmed_at": "2024-04-18T14:30:00",
                "batch_id": "batch-xyz789",
                "status": "confirmed",
                "total_transactions": 24,
                "total_ingresos": 15000.50,
                "total_gastos": 8500.75,
                "week_number": 16,
                "display_name": "Semana 16 - 2024"
            }
        }
