from pydantic import BaseModel, ConfigDict, Field


class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username, 3-50 characters")

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password, at least 8 characters")
    initial_bank: int = Field(default=0, ge=0, description="Initial bank balance in cents")
    initial_cash: int = Field(default=0, ge=0, description="Initial cash balance in cents")

    model_config = ConfigDict(from_attributes=True)

class User(UserBase):
    id: int
    is_active: bool
    bank_balance: int
    cash_balance: int

    model_config = ConfigDict(from_attributes=True)

class Token(BaseModel):
    access_token: str
    token_type: str

    model_config = ConfigDict(from_attributes=True)
