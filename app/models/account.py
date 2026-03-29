"""
Account and Credit Card models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .enums import AccountType, Currency


class AccountBase(BaseModel):
    """Base account schema"""
    name: str = Field(..., min_length=1, description="Account name")
    account_type: AccountType = Field(..., description="Type of account")
    currency: Currency = Field(default=Currency.ARS, description="Account currency")
    balance: float = Field(default=0.0, description="Current balance")
    bank_name: Optional[str] = Field(None, description="Bank name if applicable")
    account_number: Optional[str] = Field(None, description="Account number (last 4 digits)")
    is_active: bool = Field(default=True, description="Whether account is active")
    notes: Optional[str] = Field(None, description="Additional notes")


class AccountCreate(AccountBase):
    """Schema for creating account"""
    pass


class Account(AccountBase):
    """Complete account model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique account ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CreditCardBase(BaseModel):
    """Base credit card schema"""
    name: str = Field(..., min_length=1, description="Card nickname")
    bank_name: str = Field(..., description="Issuing bank")
    last_four_digits: str = Field(..., min_length=4, max_length=4, description="Last 4 digits")
    credit_limit: float = Field(..., gt=0, description="Credit limit")
    current_balance: float = Field(default=0.0, description="Current balance owed")
    closing_day: int = Field(..., ge=1, le=31, description="Statement closing day")
    due_day: int = Field(..., ge=1, le=31, description="Payment due day")
    currency: Currency = Field(default=Currency.ARS, description="Card currency")
    is_active: bool = Field(default=True, description="Whether card is active")
    notes: Optional[str] = Field(None, description="Additional notes")


class CreditCardCreate(CreditCardBase):
    """Schema for creating credit card"""
    pass


class CreditCard(CreditCardBase):
    """Complete credit card model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique card ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def available_credit(self) -> float:
        """Calculate available credit"""
        return self.credit_limit - self.current_balance
