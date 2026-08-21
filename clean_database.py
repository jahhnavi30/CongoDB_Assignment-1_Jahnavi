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
        result = session.run("""
            MATCH (n)
            DETACH DELETE n
        """)

        # Make sure the transaction is consumed
        result.consume()

    print("✅ CognoDB database cleaned successfully.")

finally:
    driver.close()