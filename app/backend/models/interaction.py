from pydantic import BaseModel, EmailStr, Field
from typing import Optional
import uuid

class InteractionBase(BaseModel):
    interaction_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    person_email: EmailStr
    type: str
    notes: str
    date: str

class InteractionCreate(InteractionBase):
    pass