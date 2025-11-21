from pydantic import BaseModel, EmailStr, Field
from typing import Optional

# Each Pydantic model corresponds to a MongoDB collection with the lowercase class name.
# Example: class Lead -> collection name "lead"

class Lead(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=120)
    contact_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    sector: Optional[str] = Field(None, description="Secteur d'activité: EHPAD, GMS, Restauration, Collectivités, etc.")
    city: Optional[str] = Field(None, max_length=120)
    waste_volume: Optional[str] = Field(None, description="Volume de biodéchets (kg/semaine)")
    message: Optional[str] = Field(None, max_length=2000)
