from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class LeadBase(BaseModel):
    lead_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    value: float
    status: str = 'Discovery'
    company_name: str
    contact_email: EmailStr

class LeadCreate(LeadBase):
    pass