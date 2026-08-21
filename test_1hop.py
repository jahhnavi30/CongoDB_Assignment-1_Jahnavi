import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

TEST_USER_ID = 30

driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)

try:
    driver.verify_connectivity()

    with driver.session() as session:

        result = session.run(
            """
            MATCH (u:User {id: $user_id})-[:VOTED_FOR]->(neighbor)
            RETURN neighbor.id AS neighbor_id
            ORDER BY neighbor.id
            """,
            user_id=TEST_USER_ID
        )

        neighbors = [
            record["neighbor_id"]
            for record in result
        ]

        print("User:", TEST_USER_ID)
        print("Number of 1-hop neighbors:", len(neighbors))
        print("Neighbors:", neighbors)

finally:
    driver.close()