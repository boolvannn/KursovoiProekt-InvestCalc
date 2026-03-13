from pydantic import BaseModel, EmailStr, Field
from typing import List

# ---- Auth ----
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    class Config: from_attributes = True

# ---- Calc ----
class CalcInput(BaseModel):
    initial_amount: float = Field(ge=0)
    monthly_contribution: float = Field(ge=0)
    annual_rate: float
    years: int = Field(ge=1, le=60)

class YearRow(BaseModel):
    year: int
    total: float
    contributions: float
    profit: float

class CalcResult(BaseModel):
    final_amount: float
    total_contributions: float
    profit: float
    schedule: List[YearRow]

class CalcCreate(CalcInput):
    title: str

class CalcOut(CalcCreate):
    id: int
    final_amount: float
    total_contributions: float
    profit: float
    schedule: List[YearRow]
    class Config: from_attributes = True
