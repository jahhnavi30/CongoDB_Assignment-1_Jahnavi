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


def create_test_graph():
    with driver.session() as session:
        session.run("""
            MATCH (n)
            DETACH DELETE n
        """)

        session.run("""
            CREATE (a:Person {name: "Alice"})
            CREATE (b:Person {name: "Bob"})
            CREATE (c:Person {name: "Charlie"})

            CREATE (a)-[:FRIENDS_WITH]->(b)
            CREATE (b)-[:FRIENDS_WITH]->(c)
        """)


def read_test_graph():
    with driver.session() as session:
        result = session.run("""
            MATCH (p:Person)-[:FRIENDS_WITH]->(friend:Person)
            RETURN p.name AS person, friend.name AS friend
            ORDER BY person
        """)

        for record in result:
            print(
                f"{record['person']} -> {record['friend']}"
            )


try:
    driver.verify_connectivity()

    print("Connected to CognoDB!")

    create_test_graph()

    print("\nTest graph created successfully.\n")

    read_test_graph()

finally:
    driver.close()