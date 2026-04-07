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
    
@router.delete("/{company_id}")
async def delete_company(company_id: str):
    query = """
    MATCH (c:Company {company_id: $company_id})
    SET c.is_deleted = true, c.deleted_at = datetime()
    RETURN COUNT(c) AS deleted_count
    """
    async with db.get_session() as session:
        result = await session.run(query, {"company_id": company_id})
        record = await result.single()
        if record["deleted_count"] == 0:
            raise HTTPException(status_code=404, detail="Company not found")
        return {"message": "Company deleted successfully"}