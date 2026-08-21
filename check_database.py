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

        # Count nodes separately
        node_result = session.run("""
            MATCH (n)
            RETURN count(n) AS nodes
        """)

        node_record = node_result.single()
        node_count = node_record["nodes"]

        # Count relationships separately
        relationship_result = session.run("""
            MATCH ()-[r]->()
            RETURN count(r) AS relationships
        """)

        relationship_record = relationship_result.single()
        relationship_count = relationship_record["relationships"]

        print("========== COGNODB DATABASE VERIFICATION ==========")
        print(f"Nodes: {node_count:,}")
        print(f"Relationships: {relationship_count:,}")

finally:
    driver.close()