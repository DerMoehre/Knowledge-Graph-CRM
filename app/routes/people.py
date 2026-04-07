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
    async with db.get_session() as session:
        result = await session.run(query, person.dict())
        record = await result.single()
        if not record:
            raise HTTPException(status_code=500, detail="Failed to create person")
        return {"message": "Person and Company linked successfully"}
    
@router.delete("/{person_id}")
async def delete_person(person_id: str):
    query = """
    MATCH (p:Person {person_id: $person_id})
    SET p.is_deleted = true, p.deleted_at = datetime()
    RETURN COUNT(p) AS deleted_count
    """
    async with db.get_session() as session:
        result = await session.run(query, {"person_id": person_id})
        record = await result.single()
        if record["deleted_count"] == 0:
            raise HTTPException(status_code=404, detail="Person not found")
        return {"message": "Person deleted successfully"}
    
@router.get("/path-finder")
async def find_network_path(start_mail: str, target_mail: str):
    query = """
    MATCH (start:Person {email: $start_email}), (target:Person {email: $target_email})
    MATCH path = shortestPath((start)-[*..8]-(target))
    RETURN path
    """
    async with db.get_session() as session:
        result = await session.run(query, {
            "start_email": start_mail, 
            "target_email": target_mail
        })
        record = await result.single()
        
        if not record:
            raise HTTPException(
                status_code=404, 
                detail="No path found. The network might be disconnected or one email is missing."
            )
            
        path = record["path"]
        
        readable_path = []
        for node in path.nodes:
            # Get the primary label (Person, Company, etc.)
            node_type = list(node.labels)[0]
            # Get the display name (Name for people, Title for Leads, Name for Companies)
            display_name = node.get("name") or node.get("title")
            
            readable_path.append({
                "type": node_type,
                "name": display_name,
                "job_title": node.get("job_title", "N/A")
            })
            
        return {
            "start": start_mail,
            "target": target_mail,
            "hops": len(path.relationships),
            "path": readable_path
        }