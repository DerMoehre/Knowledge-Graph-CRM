from fastapi import APIRouter, Security, HTTPException
from app.models.interaction import InteractionCreate
from app.database import db
from main import get_api_key

router = APIRouter(prefix="/interactions", tags=["Interactions"])

@router.post("/", dependencies=[Security(get_api_key)])
async def upsert_interaction(interaction: InteractionCreate):
    query = """
    MATCH (p:Person {email: $person_email})
    CREATE (i:Interaction {type: $type, notes: $notes, date: $date})
    MERGE (p)-[:PARTICIPATED_IN]->(i)
    RETURN i
    """
    async with db.get_session() as session:
        result = await session.run(query, interaction.model_dump())
        record = await result.single()
        if not record:
            raise HTTPException(status_code=500, detail="Failed to create interaction")
        return {"message": "Interaction created successfully"}
