from fastapi import APIRouter, HTTPException
from app.models.person import PersonCreate
from app.database import db

router = APIRouter(prefix="/people", tags=["People"])

@router.post("/")
async def upsert_person(person: PersonCreate):
    query = """
    MERGE (p:Person {email: $email})
    SET p.name = $name, p.job_title = $job_title
    MERGE (c:Company {name: $company_name})
    MERGE (p)-[r:WORKS_AT]->(c)
    RETURN p, c
    """
    async with await db.get_session() as session:
        result = await session.run(query, person.dict())
        record = await result.single()
        if not record:
            raise HTTPException(status_code=500, detail="Failed to create person")
        return {"message": "Person and Company linked successfully"}