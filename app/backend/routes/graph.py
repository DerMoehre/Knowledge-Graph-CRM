from fastapi import APIRouter, HTTPException
from models.interaction import InteractionCreate
from database import db

router = APIRouter(prefix="/graph", tags=["Graph"])

@router.get("/full")
async def get_full_graph():
    query = """
    MATCH (n)-[r]->(m)
    RETURN n, r, m LIMIT 200
    """
    async with db.get_session() as session:
        result = await session.run(query)
        graph_data = []

        async for record in result:
            graph_data.append({
                "source": {
                    "id": record["n"].get("person_id") or record["n"].get("company_id") or str(record["n"].id),
                    "name": record["n"].get("name") or record["n"].get("title", "Unknown"),
                    "label": list(record["n"].labels)[0] if record["n"].labels else "Node"
                },
                "target": {
                    "id": record["m"].get("person_id") or record["m"].get("company_id") or str(record["m"].id),
                    "name": record["m"].get("name") or record["m"].get("title", "Unknown"),
                    "label": list(record["m"].labels)[0] if record["m"].labels else "Node"
                },
                "relationship": record["r"].type
            })

    return {"graph": graph_data}
