import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


try:
    driver.verify_connectivity()

    with driver.session() as session:
        session.run("""
            CREATE INDEX user_id_index IF NOT EXISTS
            FOR (u:User)
            ON (u.id)
        """).consume()

    print("✅ User ID index created successfully.")

finally:
    driver.close()