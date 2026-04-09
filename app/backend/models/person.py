from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class PersonBase(BaseModel):
    person_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    email: EmailStr
    job_title: Optional[str] = None

class PersonCreate(PersonBase):
    company_name: str  