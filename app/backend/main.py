from fastapi import FastAPI, Security, HTTPException, status
from fastapi.security.api_key import APIKeyHeader
from contextlib import asynccontextmanager
import os
from routes import company, interaction, lead
from database import db
from routes import people

api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
API_KEY = os.getenv("APP_API_KEY")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Neo4j
    await db.connect()
    yield
    # Shutdown: Close connection
    await db.close()

async def get_api_key(api_key_header: str = Security(api_key_header)):
    if api_key_header == API_KEY:
        return api_key_header
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid API Key",
        headers={"WWW-Authenticate": "API Key"},
    )

app = FastAPI(
    title="Knowledge-Graph-CRM", lifespan=lifespan,
    components={
        "securitySchemes": {
            "ApiKeyAuth": {
                "type": "apiKey",
                "in": "header",
                "name": "X-API-KEY"
            }
        }
    },
    dependencies=[Security(get_api_key)]    
    )

# Routes
app.include_router(people.router)
app.include_router(company.router)
app.include_router(interaction.router)
app.include_router(lead.router)

@app.get("/")
async def health_check():
    return {"status": "online", "database": "connected"}