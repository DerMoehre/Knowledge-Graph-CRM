from fastapi import APIRouter, Security, HTTPException
from app.models.company import CompanyCreate
from app.database import db
from main import get_api_key

router = APIRouter(prefix="/companies", tags=["Companies"])

@router.post("/", dependencies=[Security(get_api_key)])
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