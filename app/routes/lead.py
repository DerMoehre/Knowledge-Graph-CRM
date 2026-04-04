from fastapi import APIRouter, HTTPException
from app.models.lead import LeadCreate
from app.database import db

router = APIRouter(prefix="/leads", tags=["Leads"])

@router.post("/")
async def upsert_lead(lead: LeadCreate):
    query = """
    MATCH (c:Company {name: $company_name})
    MATCH (p:Person {email: $contact_email})

    CREATE (l:Lead {
        title: $title,
        value: $value,
        status: $status,
        created_at: datetime()
    })

    MERGE (c)-[:HAS_OPPORTUNITY]->(l)
    MERGE (p)-[:STAKEHOLDER_FOR]->(l)

    RETURN l.title as title, c.name as company, p.name as contact
    """
    async with await db.get_session() as session:
        result = await session.run(query, lead.model_dump())
        record = await result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Could not create Lead. Ensure both Company and Person (Stakeholder) already exist.")
        return {
            "message": f"Lead '{record['title']}' created successfully",
            "linked_to": record['company'],
            "stakeholder": record['contact']
        }