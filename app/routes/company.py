from fastapi import APIRouter, HTTPException
from app.models.company import CompanyCreate
from app.database import db

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/")
async def upsert_company(company: CompanyCreate):
    query = """
    MERGE (c:Company {name: $name})
    SET c.industry = $industry, c.website = $website
    RETURN c
    """
    async with db.get_session() as session:
        result = await session.run(query, company.model_dump())
        record = await result.single()
        if not record:
            raise HTTPException(status_code=500, detail="Failed to create company")
        return {"message": "Company created successfully"}