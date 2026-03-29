"""
Category, RecurringExpense and Budget models
"""
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from .enums import Currency, TransactionType


class CategoryBase(BaseModel):
    """Base category schema"""
    name: str = Field(..., min_length=1, description="Category name")
    parent_id: Optional[str] = Field(None, description="Parent category ID for subcategories")
    color: Optional[str] = Field(None, description="Color code for UI (hex)")
    icon: Optional[str] = Field(None, description="Icon name or emoji")
    description: Optional[str] = Field(None, description="Category description")
    is_active: bool = Field(default=True, description="Whether category is active")


class CategoryCreate(CategoryBase):
    """Schema for creating category"""
    pass


class Category(CategoryBase):
    """Complete category model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique category ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class RecurringExpenseBase(BaseModel):
    """Base recurring expense schema"""
    name: str = Field(..., min_length=1, description="Expense name")
    amount: float = Field(..., gt=0, description="Expected amount")
    currency: Currency = Field(default=Currency.ARS, description="Currency")
    category_id: Optional[str] = Field(None, description="Associated category")
    account_id: Optional[str] = Field(None, description="Associated account")
    credit_card_id: Optional[str] = Field(None, description="Associated credit card")
    frequency: str = Field(..., description="Frequency: daily, weekly, monthly, yearly")
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date if applicable")
    is_active: bool = Field(default=True, description="Whether recurring expense is active")
    notes: Optional[str] = Field(None, description="Additional notes")


class RecurringExpenseCreate(RecurringExpenseBase):
    """Schema for creating recurring expense"""
    pass


class RecurringExpense(RecurringExpenseBase):
    """Complete recurring expense model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique recurring expense ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class BudgetBase(BaseModel):
    """Base budget schema"""
    name: str = Field(..., min_length=1, description="Budget name")
    category_ids: List[str] = Field(default_factory=list, description="Categories included")
    amount: float = Field(..., gt=0, description="Budget limit")
    currency: Currency = Field(default=Currency.ARS, description="Currency")
    period: str = Field(..., description="Period: monthly, quarterly, yearly")
    start_date: datetime = Field(..., description="Start date")
    end_date: Optional[datetime] = Field(None, description="End date if applicable")
    is_active: bool = Field(default=True, description="Whether budget is active")
    alert_threshold: Optional[float] = Field(None, ge=0, le=100, description="Alert at % of budget")


class BudgetCreate(BudgetBase):
    """Schema for creating budget"""
    pass


class Budget(BudgetBase):
    """Complete budget model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique budget ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
