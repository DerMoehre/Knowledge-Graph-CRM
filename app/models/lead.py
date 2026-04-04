from pydantic import BaseModel, EmailStr
from typing import Optional

class LeadBase(BaseModel):
    title: str
    value: float
    status: str = 'Discovery'
    company_name: str
    contact_email: EmailStr

class LeadCreate(LeadBase):
    pass