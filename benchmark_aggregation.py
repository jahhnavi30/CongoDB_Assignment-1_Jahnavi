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


QUERY = """
MATCH (u:User)-[:VOTED_FOR]->(v:User)
RETURN u.id AS user_id, count(v) AS vote_count
ORDER BY vote_count DESC
LIMIT 10
"""


WARMUP_RUNS = 10
MEASURED_RUNS = 100


def run_query(session):

    start = time.perf_counter()

    result = session.run(QUERY)

    records = list(result)

    end = time.perf_counter()

    latency_ms = (end - start) * 1000

    return latency_ms, records


try:

    driver.verify_connectivity()

    with driver.session() as session:

        print("==========================================")
        print("AGGREGATION BENCHMARK")
        print("==========================================")

        print("\nRunning warm-up...")

        for _ in range(WARMUP_RUNS):
            run_query(session)

        print(
            f"Warm-up completed: "
            f"{WARMUP_RUNS} runs"
        )

        latencies = []

        print("\nRunning measured queries...")

        for _ in range(MEASURED_RUNS):

            latency, records = run_query(session)

            latencies.append(latency)

        sorted_latencies = sorted(latencies)

        p50 = statistics.median(sorted_latencies)

        p95_index = int(
            0.95 * len(sorted_latencies)
        ) - 1

        p95 = sorted_latencies[p95_index]

        average = statistics.mean(latencies)
        minimum = min(latencies)
        maximum = max(latencies)

        print("\n==========================================")
        print("RESULTS")
        print("==========================================")

        print(f"Runs       : {MEASURED_RUNS}")
        print(f"Average    : {average:.3f} ms")
        print(f"p50        : {p50:.3f} ms")
        print(f"p95        : {p95:.3f} ms")
        print(f"Minimum    : {minimum:.3f} ms")
        print(f"Maximum    : {maximum:.3f} ms")

        print("\nTop 10 users from final query:")

        for record in records:
            print(
                f"User {record['user_id']} "
                f"→ {record['vote_count']} votes"
            )

finally:

    driver.close()
    