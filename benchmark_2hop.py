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
# 2-hop query
# --------------------------------------------------

QUERY = """
MATCH (u:User {id: $user_id})
      -[:VOTED_FOR]->()
      -[:VOTED_FOR]->(neighbor)

RETURN DISTINCT neighbor.id AS neighbor_id
"""


# Use the same users as the 1-hop benchmark
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


def run_query(session, user_id):

    start = time.perf_counter()

    result = session.run(
        QUERY,
        user_id=user_id
    )

    # Consume the complete result
    records = list(result)

    end = time.perf_counter()

    latency_ms = (end - start) * 1000

    return latency_ms, len(records)


try:

    driver.verify_connectivity()

    with driver.session() as session:

        print("==========================================")
        print("2-HOP TRAVERSAL BENCHMARK")
        print("==========================================")

        # --------------------------------------
        # Warm-up
        # --------------------------------------

        print("\nRunning warm-up...")

        for i in range(WARMUP_RUNS):

            user_id = TEST_USERS[i % len(TEST_USERS)]

            run_query(
                session,
                user_id
            )

        print(
            f"Warm-up completed: "
            f"{WARMUP_RUNS} runs"
        )

        # --------------------------------------
        # Measurement
        # --------------------------------------

        latencies = []
        result_counts = []

        print("\nRunning measured queries...")

        for i in range(MEASURED_RUNS):

            user_id = TEST_USERS[i % len(TEST_USERS)]

            latency, result_count = run_query(
                session,
                user_id
            )

            latencies.append(latency)
            result_counts.append(result_count)

        # --------------------------------------
        # Statistics
        # --------------------------------------

        p50 = statistics.median(latencies)

        sorted_latencies = sorted(latencies)

        p95_index = int(
            0.95 * len(sorted_latencies)
        ) - 1

        p95 = sorted_latencies[p95_index]

        average = statistics.mean(latencies)

        minimum = min(latencies)

        maximum = max(latencies)

        # --------------------------------------
        # Results
        # --------------------------------------

        print("\n==========================================")
        print("RESULTS")
        print("==========================================")

        print(f"Runs       : {MEASURED_RUNS}")
        print(f"Average    : {average:.3f} ms")
        print(f"p50        : {p50:.3f} ms")
        print(f"p95        : {p95:.3f} ms")
        print(f"Minimum    : {minimum:.3f} ms")
        print(f"Maximum    : {maximum:.3f} ms")

        print("\nExample result counts:")
        print(result_counts[:10])


finally:

    driver.close()