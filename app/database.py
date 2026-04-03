import os
from neo4j import AsyncGraphDatabase

class Neo4jDatabase:
    def __init__(self):
        self.driver = None

    async def connect(self):
        uri = os.getenv("NEO4J_URI", "bolt://database:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password123")
        self.driver = AsyncGraphDatabase.driver(uri, auth=(user, password))

    async def close(self):
        if self.driver:
            await self.driver.close()

    async def get_session(self):
        return self.driver.session()

db = Neo4jDatabase()