from fastapi import APIRouter, HTTPException
from typing import Optional
from models.company import CompanyCreate, CompanyOut
from database import db

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
    
@router.get("/", response_model=list[CompanyOut])
async def get_companies(
    company_id: Optional[str] = None,
    name: Optional[str] = None,
    include_deleted: bool = False
):
    query = """
    MATCH (c:Company)
    WHERE ($include_deleted = true OR c.is_deleted IS NULL OR c.is_deleted = false)
      AND ($company_id IS NULL OR c.company_id = $company_id)
      AND ($name IS NULL OR c.name = $name)
    RETURN c { .*, id: c.company_id } as company
    """
    
    params = {
        "company_id": company_id,
        "name": name,
        "include_deleted": include_deleted 
    }

    async with db.get_session() as session:
        result = await session.run(query, params)
        records = await result.values()
        return [record[0] for record in records]

@router.get("/{company_id}/details")
async def get_company_details(company_id: str):
    query = """
    MATCH (c:Company {company_id: $company_id})
    OPTIONAL MATCH (c)<-[:WORKS_AT]-(p:Person)
    OPTIONAL MATCH (c)-[:HAS_OPPORTUNITY]->(l:Lead)

    WITH c,
        collect(DISTINCT p { .name, .job_title, .email, .person_id }) as employee_list,
        collect(DISTINCT l { .title, .value, .status, .lead_id }) as lead_list
    RETURN c { 
        .*, 
        employees: employee_list,
        leads: lead_list
    } as details
    """
    async with db.get_session() as session:
        result = await session.run(query, {"company_id": company_id})
        record = await result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Company not found")
        return record["details"]