"""
Asset, Liability and Net Worth models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .enums import AssetType, LiabilityType, Currency


class AssetBase(BaseModel):
    """Base asset schema"""
    name: str = Field(..., min_length=1, description="Asset name")
    asset_type: AssetType = Field(..., description="Type of asset")
    value: float = Field(..., description="Current value")
    currency: Currency = Field(default=Currency.ARS, description="Asset currency")
    account_id: Optional[str] = Field(None, description="Linked account ID if applicable")
    description: Optional[str] = Field(None, description="Asset description")
    acquisition_date: Optional[datetime] = Field(None, description="Date acquired")
    acquisition_cost: Optional[float] = Field(None, description="Original acquisition cost")
    is_liquid: bool = Field(default=True, description="Whether easily convertible to cash")
    notes: Optional[str] = Field(None, description="Additional notes")


class AssetCreate(AssetBase):
    """Schema for creating asset"""
    pass


class Asset(AssetBase):
    """Complete asset model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique asset ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class LiabilityBase(BaseModel):
    """Base liability schema"""
    name: str = Field(..., min_length=1, description="Liability name")
    liability_type: LiabilityType = Field(..., description="Type of liability")
    balance: float = Field(..., ge=0, description="Current balance owed")
    currency: Currency = Field(default=Currency.ARS, description="Liability currency")
    credit_card_id: Optional[str] = Field(None, description="Linked credit card if applicable")
    interest_rate: Optional[float] = Field(None, ge=0, le=100, description="Annual interest rate %")
    minimum_payment: Optional[float] = Field(None, ge=0, description="Minimum monthly payment")
    due_date: Optional[int] = Field(None, ge=1, le=31, description="Payment due day of month")
    original_amount: Optional[float] = Field(None, description="Original loan/debt amount")
    start_date: Optional[datetime] = Field(None, description="Start date")
    end_date: Optional[datetime] = Field(None, description="Expected payoff date")
    notes: Optional[str] = Field(None, description="Additional notes")


class LiabilityCreate(LiabilityBase):
    """Schema for creating liability"""
    pass


class Liability(LiabilityBase):
    """Complete liability model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique liability ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class NetWorthSnapshotBase(BaseModel):
    """Base net worth snapshot schema"""
    snapshot_date: datetime = Field(..., description="Date of snapshot")
    total_assets: float = Field(..., description="Total value of all assets")
    total_liabilities: float = Field(..., description="Total value of all liabilities")
    net_worth: float = Field(..., description="Net worth (assets - liabilities)")
    currency: Currency = Field(default=Currency.ARS, description="Snapshot currency")
    notes: Optional[str] = Field(None, description="Notes about this snapshot")


class NetWorthSnapshotCreate(NetWorthSnapshotBase):
    """Schema for creating net worth snapshot"""
    pass


class NetWorthSnapshot(NetWorthSnapshotBase):
    """Complete net worth snapshot model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique snapshot ID")
    created_at: datetime = Field(default_factory=datetime.now)

    @classmethod
    def calculate(cls, total_assets: float, total_liabilities: float, currency: Currency = Currency.ARS):
        """Helper method to create snapshot with calculated net worth"""
        return cls(
            snapshot_date=datetime.now(),
            total_assets=total_assets,
            total_liabilities=total_liabilities,
            net_worth=total_assets - total_liabilities,
            currency=currency
        )
