import os
import time
import statistics

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


# --------------------------------------------------
# Fixed test users
# --------------------------------------------------

TEST_USERS = [
    3,
    30,
    50,
    100,
    200,
    500,
    1000,
    2000,
    3000,
    4000
]


WARMUP_RUNS = 10
MEASURED_RUNS = 100


# --------------------------------------------------
# Read query
# --------------------------------------------------

READ_QUERY = """
MATCH (u:User {id: $user_id})-[:VOTED_FOR]->(neighbor)
RETURN neighbor.id AS neighbor_id
"""


# --------------------------------------------------
# Temporary write
# --------------------------------------------------

WRITE_QUERY = """
MATCH (source:User {id: $source_id})
MATCH (target:User {id: $target_id})
MERGE (source)-[:BENCHMARK_TEMP]->(target)
"""


# --------------------------------------------------
# Remove temporary write
# --------------------------------------------------

DELETE_QUERY = """
MATCH (source:User {id: $source_id})
      -[r:BENCHMARK_TEMP]->
      (target:User {id: $target_id})
DELETE r
"""


def mixed_operation(session, source_id, target_id):

    start = time.perf_counter()

    # -----------------------------
    # READ
    # -----------------------------

    result = session.run(
        READ_QUERY,
        user_id=source_id
    )

    list(result)

    # -----------------------------
    # WRITE
    # -----------------------------

    session.run(
        WRITE_QUERY,
        source_id=source_id,
        target_id=target_id
    ).consume()

    # -----------------------------
    # SECOND READ
    # -----------------------------

    result = session.run(
        """
        MATCH (u:User {id: $user_id})
        RETURN u.id AS user_id
        """,
        user_id=target_id
    )

    list(result)

    # -----------------------------
    # CLEANUP WRITE
    # -----------------------------

    session.run(
        DELETE_QUERY,
        source_id=source_id,
        target_id=target_id
    ).consume()

    end = time.perf_counter()

    return (end - start) * 1000


try:

    driver.verify_connectivity()

    with driver.session() as session:

        print("==========================================")
        print("MIXED READ/WRITE BENCHMARK")
        print("==========================================")

        # --------------------------------------------------
        # Warm-up
        # --------------------------------------------------

        print("\nRunning warm-up...")

        for i in range(WARMUP_RUNS):

            source_id = TEST_USERS[
                i % len(TEST_USERS)
            ]

            target_id = TEST_USERS[
                (i + 1) % len(TEST_USERS)
            ]

            mixed_operation(
                session,
                source_id,
                target_id
            )

        print(
            f"Warm-up completed: "
            f"{WARMUP_RUNS} runs"
        )

        # --------------------------------------------------
        # Measurement
        # --------------------------------------------------

        latencies = []

        print("\nRunning measured queries...")

        for i in range(MEASURED_RUNS):

            source_id = TEST_USERS[
                i % len(TEST_USERS)
            ]

            target_id = TEST_USERS[
                (i + 1) % len(TEST_USERS)
            ]

            latency = mixed_operation(
                session,
                source_id,
                target_id
            )

            latencies.append(latency)

        # --------------------------------------------------
        # Statistics
        # --------------------------------------------------

        sorted_latencies = sorted(latencies)

        p50 = statistics.median(
            sorted_latencies
        )

        p95_index = int(
            0.95 * len(sorted_latencies)
        ) - 1

        p95 = sorted_latencies[
            p95_index
        ]

        average = statistics.mean(
            latencies
        )

        minimum = min(latencies)
        maximum = max(latencies)

        # --------------------------------------------------
        # Results
        # --------------------------------------------------

        print("\n==========================================")
        print("RESULTS")
        print("==========================================")

        print(f"Runs       : {MEASURED_RUNS}")
        print(f"Average    : {average:.3f} ms")
        print(f"p50        : {p50:.3f} ms")
        print(f"p95        : {p95:.3f} ms")
        print(f"Minimum    : {minimum:.3f} ms")
        print(f"Maximum    : {maximum:.3f} ms")

finally:

    driver.close()