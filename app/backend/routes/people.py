from fastapi import APIRouter, HTTPException
from models.person import PersonCreate
from database import db

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
    
@router.get("/{person_id}/details")
async def get_person_details(person_id: str):
    query = """
    MATCH (p:Person {person_id: $person_id})
    OPTIONAL MATCH (p)-[:WORKS_AT]->(c:Company)
    OPTIONAL MATCH (p)-[:PARTICIPATED_IN]->(i:Interaction)
    OPTIONAL MATCH (p)-[:STAKEHOLDER_FOR]->(l:Lead)

    WITH p, c,
        collect(DISTINCT i { .type, .notes, .date }) as interaction_list,
        collect(DISTINCT l { .title, .value, .status }) as lead_list
    RETURN p { 
        .*, 
        company: c { .name, .industry, .website, .company_id },
        interactions: interaction_list,
        leads: lead_list
    } as details
    """
    async with db.get_session() as session:
        result = await session.run(query, {"person_id": person_id})
        record = await result.single()
        if not record:
            raise HTTPException(status_code=404, detail="Person not found")
        return record["details"]
    
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