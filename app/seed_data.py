import asyncio
from faker import Faker
from app.database import db
import random
import logging

fake = Faker()
logging.basicConfig(level=logging.INFO)

async def create_interconnections(session, companies):
    logging.info("Creating strategic company partnerships...")

    for _ in range(3):
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
    logging.info("Connecting to database...")
    await db.connect()

    logging.info("Starting database seeding...")

    companies = [fake.company() for _ in range(5)]
    try:
        async with await db.get_session() as session:
            for company_name in companies:
                logging.info(f"Creating {company_name} and its employees...")

                for _ in range(random.randint(2, 5)):
                    person = {
                        "name": fake.name(),
                        "email": fake.unique.email(),
                        "job_title": fake.job(),
                        "company_name": company_name
                    }

                    query_person = """
                    MERGE (c:Company {name: $company_name})
                    MERGE (p:Person {email: $email})
                    SET p.name = $name, p.job_title = $job_title
                    MERGE (p)-[:WORKS_AT]->(c)
                    RETURN p.email as email
                    """
                    await session.run(query_person, person)

                    if random.random() > 0.5:
                        interaction = {
                            "email": person["email"],
                            "type": random.choice(["Call", "Email", "Meeting"]),
                            "notes": fake.sentence(),
                            "date": fake.date_time_this_year().isoformat()
                        }
                        query_interaction = """
                        MATCH (p:Person {email: $email})
                        CREATE (i:Interaction {type: $type, notes: $notes, date: $date})
                        MERGE (p)-[:PARTICIPATED_IN]->(i)
                        """
                        await session.run(query_interaction, interaction)

            logging.info("Creating pipeline leads...")
            for _ in range(3):
                pick_query = "MATCH (p:Person)-[:WORKS_AT]->(c:Company) RETURN p.email as email, c.name as company ORDER BY rand() LIMIT 1"
                result = await session.run(pick_query)
                record = await result.single()

                lead = {
                    "title": f"{fake.word().capitalize()} Implementation",
                    "value": random.randint(10000, 90000),
                    "company_name": record["company"],
                    "contact_email": record["email"]
                }

                query_lead = """
                MATCH (c:Company {name: $company_name})
                MATCH (p:Person {email: $contact_email})
                CREATE (l:Lead {title: $title, value: $value, status: 'Discovery', created_at: datetime()})
                MERGE (c)-[:HAS_OPPORTUNITY]->(l)
                MERGE (p)-[:STAKEHOLDER_FOR]->(l)
                """
                await session.run(query_lead, lead)

            await create_interconnections(session, companies)
            logging.info("Database seeding completed")
    finally:
        logging.info("Closing database connection...")
        await db.close()

if __name__ == "__main__":
    asyncio.run(seed_database())