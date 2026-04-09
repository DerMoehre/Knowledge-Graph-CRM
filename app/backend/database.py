import os
from neo4j import AsyncGraphDatabase

class Neo4jDatabase:
    def __init__(self):
        self.driver = None
        self.uri = None
        self.user = None
        self.password = None

    async def connect(self):
        """Initialize the Neo4j driver"""
        if not self.driver:
            self.uri = os.getenv("NEO4J_URI")
            self.user = os.getenv("NEO4J_USERNAME")
            self.password = os.getenv("NEO4J_PASSWORD")
            if not self.uri:
                raise RuntimeError("NEO4J_URI is missing or invalid. Check your .env file.")

            self.driver = AsyncGraphDatabase.driver(
                self.uri.strip(), 
                auth=(self.user.strip(), self.password.strip())
            )

    async def close(self):
        """Close the Neo4j driver when the app stops"""
        if self.driver:
            await self.driver.close()
            self.driver = None

    def get_session(self):
        """Retuns a session and raises an error if connect was not successful"""
        if self.driver is None:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return self.driver.session()

db = Neo4jDatabase()