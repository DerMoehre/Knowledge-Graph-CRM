from fastapi import APIRouter, HTTPException
from app.models.interaction import InteractionCreate
from app.database import db

router = APIRouter(prefix="/interactions", tags=["Interactions"])

@router.post("/")
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
@router.delete("/{interaction_id}")
async def delete_interaction(interaction_id: str):
    query = """
    MATCH (i:Interaction {interaction_id: $interaction_id})
    SET i.is_deleted = true, i.deleted_at = datetime()
    RETURN COUNT(i) AS deleted_count
    """
    async with db.get_session() as session:
        result = await session.run(query, {"interaction_id": interaction_id})
        record = await result.single()
        if record["deleted_count"] == 0:
            raise HTTPException(status_code=404, detail="Interaction not found")
        return {"message": "Interaction deleted successfully"}