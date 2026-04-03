from pydantic import BaseModel, EmailStr
from typing import Optional

class PersonBase(BaseModel):
    name: str
    email: EmailStr
    job_title: Optional[str] = None

class PersonCreate(PersonBase):
    company_name: str  