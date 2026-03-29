"""
Cryptocurrency wallet and position models
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from .enums import CryptoNetwork, Currency


class CryptoWalletBase(BaseModel):
    """Base crypto wallet schema"""
    name: str = Field(..., min_length=1, description="Wallet name/nickname")
    network: CryptoNetwork = Field(..., description="Blockchain network")
    address: str = Field(..., min_length=1, description="Wallet address")
    wallet_type: str = Field(..., description="Type: hot, cold, exchange, hardware")
    is_active: bool = Field(default=True, description="Whether wallet is active")
    notes: Optional[str] = Field(None, description="Additional notes")


class CryptoWalletCreate(CryptoWalletBase):
    """Schema for creating crypto wallet"""
    pass


class CryptoWallet(CryptoWalletBase):
    """Complete crypto wallet model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique wallet ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CryptoPositionBase(BaseModel):
    """Base crypto position schema"""
    wallet_id: str = Field(..., description="Associated wallet ID")
    token_symbol: str = Field(..., min_length=1, description="Token symbol (BTC, ETH, etc)")
    token_name: Optional[str] = Field(None, description="Full token name")
    contract_address: Optional[str] = Field(None, description="Token contract address if ERC20/BEP20")
    quantity: float = Field(..., gt=0, description="Amount of tokens held")
    average_buy_price: Optional[float] = Field(None, description="Average acquisition price")
    price_currency: Currency = Field(default=Currency.USD, description="Currency of price")
    current_price: Optional[float] = Field(None, description="Current market price")
    total_value: Optional[float] = Field(None, description="Total position value")
    last_price_update: Optional[datetime] = Field(None, description="Last price update timestamp")
    notes: Optional[str] = Field(None, description="Additional notes")


class CryptoPositionCreate(CryptoPositionBase):
    """Schema for creating crypto position"""
    pass


class CryptoPosition(CryptoPositionBase):
    """Complete crypto position model"""
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Unique position ID")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @property
    def unrealized_pnl(self) -> Optional[float]:
        """Calculate unrealized profit/loss"""
        if self.average_buy_price and self.current_price:
            cost_basis = self.quantity * self.average_buy_price
            current_value = self.quantity * self.current_price
            return current_value - cost_basis
        return None

    @property
    def unrealized_pnl_percentage(self) -> Optional[float]:
        """Calculate unrealized profit/loss percentage"""
        if self.average_buy_price and self.current_price:
            return ((self.current_price - self.average_buy_price) / self.average_buy_price) * 100
        return None
