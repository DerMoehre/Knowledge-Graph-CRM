from pydantic import BaseModel, Field
from typing import Optional
import uuid

class CompanyBase(BaseModel):
    company_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    industry: Optional[str] = None
    website: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class CompanyOut(CompanyBase):
    pass