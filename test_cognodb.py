import os

from dotenv import load_dotenv
from neo4j import GraphDatabase


# Load variables from .env
load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


# Check that credentials were loaded
if not URI:
    raise ValueError("COGNODB_URI is missing from .env")

if not USERNAME:
    raise ValueError("COGNODB_USERNAME is missing from .env")

if not PASSWORD:
    raise ValueError("COGNODB_PASSWORD is missing from .env")


# Create Neo4j driver
driver = GraphDatabase.driver(
    URI,
    auth=(USERNAME, PASSWORD)
)


try:
    # Check connection
    driver.verify_connectivity()

    print("Successfully connected to CognoDB!")

    # Run a simple Cypher query
    with driver.session() as session:
        result = session.run("RETURN 1 AS test")
        record = result.single()

        print("Cypher test result:", record["test"])


except Exception as e:
    print("Connection failed!")
    print("Error:", e)


finally:
    driver.close()