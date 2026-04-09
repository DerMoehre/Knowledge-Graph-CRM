import asyncio
from faker import Faker
from app.backend.database import db
import random
from dotenv import load_dotenv
import os
import logging
from app.backend.models.company import CompanyCreate
from app.backend.models.person import PersonCreate
from app.backend.models.interaction import InteractionCreate
from app.backend.models.lead import LeadCreate

fake = Faker()
logging.basicConfig(level=logging.INFO)
load_dotenv()  

INDUSTRIES = [
    "Technology", "Finance", "Healthcare", "Manufacturing", 
    "Energy", "Retail", "Education", "Logistics", "Telecommunications"
]

async def create_interconnections(session, companies):
    logging.info("Creating strategic company partnerships...")

    for _ in range(5):
        c1, c2 = random.sample(companies, 2)
        rel_type = random.choice(["PARTNERED_WITH", "SUBSIDIARY_OF", "SUPPLIES"])
        
        query = f"""
        MATCH (a:Company {{name: $c1}}), (b:Company {{name: $c2}})
        MERGE (a)-[:{rel_type}]->(b)
        """
        await session.run(query, {"c1": c1, "c2": c2})

    logging.info("Creating People who switched companies...")

    bridge_query = """
    MATCH (p:Person)-[:WORKS_AT]->(current:Company)
    MATCH (old:Company) WHERE old <> current
    WITH p, old ORDER BY rand() LIMIT 3
    MERGE (p)-[:PREVIOUSLY_WORKED_AT]->(old)
    """
    await session.run(bridge_query)

    logging.info("Creating the User Node...")

    me_query = """
    MERGE (u:User {email: 'me@example.com'})
    SET u.name = 'Your Name', u.job_title = 'Lead Developer'
    WITH u
    MATCH (c:Company) ORDER BY rand() LIMIT 1
    MERGE (u)-[:WORKS_AT]->(c)
    """
    await session.run(me_query)

async def seed_database():
    uri = os.getenv("NEO4J_URI")
    logging.info(f"Connecting to database at {uri}")
    await db.connect()

    logging.info("Starting database seeding...")

    companies = [fake.company() for _ in range(20)]
    try:
        async with db.get_session() as session:
            logging.info("Clearing Aura DB...")
            await session.run("MATCH (n) DETACH DELETE n")
            
            logging.info("Phase 1: Creating all companies...")
            for company_name in companies:
                company_data = CompanyCreate(name=company_name, industry=random.choice(INDUSTRIES), website=fake.url())
                params = company_data.model_dump()
                await session.run(
                """
                CREATE (c:Company {
                    company_id: $company_id, 
                    name: $name, 
                    industry: $industry, 
                    website: $website
                })
                """, 
                params
                )
            logging.info("Phase 2: Populating employees...")
            for company_name in companies:
                for _ in range(random.randint(2, 5)):
                    person_data = PersonCreate(
                        name=fake.name(),
                        email=fake.unique.email(),
                        job_title=fake.job(),
                        company_name=company_name
                    )
                    params = person_data.model_dump()
                    query_person = """
                    MATCH (c:Company {name: $company_name})
                    CREATE (p:Person {person_id: $person_id, email: $email, name: $name, job_title: $job_title})
                    CREATE (p)-[:WORKS_AT]->(c)
                    """
                    await session.run(query_person, params)

                    if random.random() > 0.5:
                        interaction_data = InteractionCreate(
                            person_email=person_data.email,
                            type=random.choice(["Email", "Call", "Meeting"]),
                            notes=fake.sentence(),
                            date=str(fake.date_time_this_year().isoformat()),
                        )
                        interaction = interaction_data.model_dump()
                        query_interaction = """
                        MATCH (p:Person {email: $person_email})
                        CREATE (i:Interaction {interaction_id: $interaction_id, type: $type, notes: $notes, date: $date})
                        MERGE (p)-[:PARTICIPATED_IN]->(i)
                        """
                        await session.run(query_interaction, interaction)

            logging.info("Creating pipeline leads...")
            for _ in range(3):
                pick_query = "MATCH (p:Person)-[:WORKS_AT]->(c:Company) RETURN p.email as email, c.name as company ORDER BY rand() LIMIT 1"
                result = await session.run(pick_query)
                record = await result.single()
                if record:
                    lead_data = LeadCreate(
                        title=f"{fake.word().capitalize()} Implementation",
                        value=random.randint(10000, 90000),
                        company_name=record["company"],
                        contact_email=record["email"]
                    )
                    lead = lead_data.model_dump()

                    query_lead = """
                    MATCH (c:Company {name: $company_name})
                    MATCH (p:Person {email: $contact_email})
                    CREATE (l:Lead {lead_id: $lead_id, title: $title, value: $value, status: 'Discovery', created_at: datetime()})
                    MERGE (c)-[:HAS_OPPORTUNITY]->(l)
                    MERGE (p)-[:STAKEHOLDER_FOR]->(l)
                    """
                    await session.run(query_lead, lead)
                else:
                    logging.warning("Could not find a person to link a lead to!")

            await create_interconnections(session, companies)
            logging.info("Database seeding completed")
    finally:
        logging.info("Closing database connection...")
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_database())