from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database import db
from app.routes import people

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Connect to Neo4j
    await db.connect()
    yield
    # Shutdown: Close connection
    await db.close()

app = FastAPI(title="Knowledge-Graph-CRM", lifespan=lifespan)

# Routes
app.include_router(people.router)

@app.get("/")
async def health_check():
    return {"status": "online", "database": "connected"}