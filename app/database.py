import os
from neo4j import AsyncGraphDatabase

class Neo4jDatabase:
    def __init__(self):
        self.driver = None
        self.uri = os.getenv("NEO4J_URI", "bolt://database:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "password123")

    async def connect(self):
        """Initialize the Neo4j driver"""
        if not self.driver:
            self.driver = AsyncGraphDatabase.driver(
                self.uri, auth=(self.user, self.password)
                )

    async def close(self):
        """Close the Neo4j driver when the app stops"""
        if self.driver:
            await self.driver.close()
            self.driver = None

    async def get_session(self):
        """Retuns a session and raises an error if connect was not successful"""
        if self.driver is None:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return self.driver.session()

db = Neo4jDatabase()