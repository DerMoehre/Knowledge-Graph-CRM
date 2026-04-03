from pydantic import BaseModel, EmailStr
from typing import Optional

class InteractionBase(BaseModel):
    person_email: EmailStr
    type: str
    notes: str
    date: str

class InteractionCreate(InteractionBase):
    pass