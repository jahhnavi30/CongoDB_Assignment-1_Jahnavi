import os
import time
from pathlib import Path

from dotenv import load_dotenv
from neo4j import GraphDatabase


# --------------------------------------------------
# Configuration
# --------------------------------------------------

load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")

DATASET_PATH = Path("data/dataset/Wiki-Vote.txt")

BATCH_SIZE = 1000


# --------------------------------------------------
# Read dataset
# --------------------------------------------------

def read_edges():
    edges = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:

            # Ignore comments and empty lines
            if line.startswith("#") or not line.strip():
                continue

            source, target = map(int, line.split())

            edges.append({
                "source": source,
                "target": target
            })

    return edges


# --------------------------------------------------
# Create users
# --------------------------------------------------

def create_users(session, edges):
    user_ids = set()

    for edge in edges:
        user_ids.add(edge["source"])
        user_ids.add(edge["target"])

    user_data = [
        {"id": user_id}
        for user_id in user_ids
    ]

    for i in range(0, len(user_data), BATCH_SIZE):

        batch = user_data[i:i + BATCH_SIZE]

        session.run(
            """
            UNWIND $users AS user
            MERGE (u:User {id: user.id})
            """,
            users=batch
        )


# --------------------------------------------------
# Create relationships
# --------------------------------------------------

def create_relationships(session, edges):

    for i in range(0, len(edges), BATCH_SIZE):

        batch = edges[i:i + BATCH_SIZE]

        session.run(
            """
            UNWIND $edges AS edge

            MATCH (source:User {id: edge.source})
            MATCH (target:User {id: edge.target})

            MERGE (source)-[:VOTED_FOR]->(target)
            """,
            edges=batch
        )

        processed = min(i + BATCH_SIZE, len(edges))

        print(
            f"Relationships loaded: "
            f"{processed:,}/{len(edges):,}"
        )


# --------------------------------------------------
# Main
# --------------------------------------------------

def main():

    print("=" * 60)
    print("CognoDB Wiki-Vote Dataset Loader")
    print("=" * 60)

    # Read dataset
    print("\nReading dataset...")

    edges = read_edges()

    print(f"Relationships found: {len(edges):,}")

    # Connect to CognoDB
    print("\nConnecting to CognoDB...")

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    driver.verify_connectivity()

    print("Connected successfully!")

    start_time = time.perf_counter()

    try:

        with driver.session() as session:

            print("\nCreating User nodes...")

            create_users(session, edges)

            print("User nodes created.")

            print("\nCreating relationships...")

            create_relationships(session, edges)

    finally:

        driver.close()

    end_time = time.perf_counter()

    total_time = end_time - start_time

    print("\n" + "=" * 60)
    print("LOAD COMPLETED")
    print("=" * 60)

    print(f"Total relationships : {len(edges):,}")
    print(f"Total load time     : {total_time:.2f} seconds")

    if total_time > 0:

        print(
            f"Relationships/sec   : "
            f"{len(edges) / total_time:,.2f}"
        )


if __name__ == "__main__":
    main()