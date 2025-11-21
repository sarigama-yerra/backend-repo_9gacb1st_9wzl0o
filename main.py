from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Any, Dict
from datetime import datetime

# Database helpers are pre-configured in this environment
# - create_document(collection_name, data)
# - get_documents(collection_name, filter_dict, limit)
try:
    from database import create_document, get_documents  # type: ignore
except Exception as e:  # pragma: no cover
    create_document = None  # type: ignore
    get_documents = None  # type: ignore

app = FastAPI(title="CompostPro API", version="1.0.0")

# CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class Lead(BaseModel):
    company_name: str = Field(..., min_length=2, max_length=120)
    contact_name: str = Field(..., min_length=2, max_length=120)
    email: EmailStr
    phone: Optional[str] = Field(None, max_length=30)
    sector: Optional[str] = Field(None, description="Secteur d'activité: EHPAD, GMS, Restauration, Collectivités, etc.")
    city: Optional[str] = Field(None, max_length=120)
    waste_volume: Optional[str] = Field(None, description="Volume de biodéchets (kg/semaine)")
    message: Optional[str] = Field(None, max_length=2000)


class LeadOut(Lead):
    id: Optional[str] = None
    created_at: Optional[datetime] = None


@app.get("/test")
async def test() -> Dict[str, Any]:
    """Simple connectivity test, including database check if available."""
    db_ok = False
    try:
        if get_documents is not None:
            _ = await get_documents("lead", {}, limit=1)
            db_ok = True
    except Exception:
        db_ok = False
    return {"status": "ok", "database": db_ok}


@app.post("/leads", response_model=Dict[str, Any])
async def create_lead(lead: Lead):
    """Store a contact request (lead) into the database."""
    if create_document is None:
        raise HTTPException(status_code=500, detail="Database module not available")

    data = lead.dict()
    try:
        inserted = await create_document("lead", data)
        return {"success": True, "id": str(inserted.get("_id", ""))}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la création: {e}")


@app.get("/leads", response_model=List[LeadOut])
async def list_leads(limit: int = 50):
    """List the most recent leads (for admin/testing)."""
    if get_documents is None:
        raise HTTPException(status_code=500, detail="Database module not available")
    try:
        docs = await get_documents("lead", filter_dict={}, limit=limit)
        # Normalize output
        normalized: List[LeadOut] = []
        for d in docs:
            item = {
                "id": str(d.get("_id")) if d.get("_id") is not None else None,
                "company_name": d.get("company_name"),
                "contact_name": d.get("contact_name"),
                "email": d.get("email"),
                "phone": d.get("phone"),
                "sector": d.get("sector"),
                "city": d.get("city"),
                "waste_volume": d.get("waste_volume"),
                "message": d.get("message"),
                "created_at": d.get("created_at"),
            }
            normalized.append(LeadOut(**item))
        return normalized
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur lors de la récupération: {e}")
