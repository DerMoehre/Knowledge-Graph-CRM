from fastapi import APIRouter, HTTPException, Query
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
    async with db.get_session() as session:
        result = await session.run(query, lead.model_dump())
        record = await result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Could not create Lead. Ensure both Company and Person (Stakeholder) already exist.")
        return {
            "message": f"Lead '{record['title']}' created successfully",
            "linked_to": record['company'],
            "stakeholder": record['contact']
        }
    
@router.get("/")
async def list_dangling_leads(min_value: float = Query(10000, alias='Lead Value')):
    query = """
    MATCH (l:Lead)<-[:STAKEHOLDER_FOR]-(p:Person)
    WHERE l.value > $min_value
    OPTIONAL MATCH (p)-[:PARTICIPATED_IN]->(i:Interaction)
    WITH l, p, max(i.date) AS last_contact
    RETURN l.title AS lead_title, p.name as stakeholder, last_contact AS last_contact
    ORDER BY last_contact ASC
    """
    async with db.get_session() as session:
        result = await session.run(query, {"min_value": min_value})
        leads = []
        async for record in result:
            leads.append({
                "lead_title": record["lead_title"],
                "stakeholder": record["stakeholder"],
                "last_contact": record["last_contact"]
            })
        return leads