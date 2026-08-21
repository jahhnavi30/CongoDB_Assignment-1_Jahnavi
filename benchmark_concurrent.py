import os
import time
import statistics
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotenv import load_dotenv
from neo4j import GraphDatabase


load_dotenv()

URI = os.getenv("COGNODB_URI")
USERNAME = os.getenv("COGNODB_USERNAME")
PASSWORD = os.getenv("COGNODB_PASSWORD")


# --------------------------------------------------
# Configuration
# --------------------------------------------------

WORKERS = 5
OPERATIONS_PER_WORKER = 20

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


# --------------------------------------------------
# Queries
# --------------------------------------------------

READ_QUERY = """
MATCH (u:User {id: $user_id})-[:VOTED_FOR]->(neighbor)
RETURN neighbor.id AS neighbor_id
"""


WRITE_QUERY = """
MATCH (source:User {id: $source_id})
MATCH (target:User {id: $target_id})
MERGE (source)-[:BENCHMARK_TEMP]->(target)
"""


DELETE_QUERY = """
MATCH (source:User {id: $source_id})
      -[r:BENCHMARK_TEMP]->
      (target:User {id: $target_id})
DELETE r
"""


# --------------------------------------------------
# One concurrent operation
# --------------------------------------------------

def worker_operation(worker_id, operation_id):

    driver = GraphDatabase.driver(
        URI,
        auth=(USERNAME, PASSWORD)
    )

    source_id = TEST_USERS[
        (worker_id + operation_id)
        % len(TEST_USERS)
    ]

    target_id = TEST_USERS[
        (worker_id + operation_id + 1)
        % len(TEST_USERS)
    ]

    start = time.perf_counter()

    try:

        with driver.session() as session:

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
            # CLEANUP
            # -----------------------------

            session.run(
                DELETE_QUERY,
                source_id=source_id,
                target_id=target_id
            ).consume()

    finally:

        driver.close()

    end = time.perf_counter()

    return (end - start) * 1000


# --------------------------------------------------
# Main benchmark
# --------------------------------------------------

def main():

    print("==========================================")
    print("CONCURRENT MIXED READ/WRITE BENCHMARK")
    print("==========================================")

    total_operations = (
        WORKERS * OPERATIONS_PER_WORKER
    )

    print(f"\nWorkers             : {WORKERS}")
    print(
        f"Operations/worker   : "
        f"{OPERATIONS_PER_WORKER}"
    )
    print(
        f"Total operations    : "
        f"{total_operations}"
    )

    print("\nRunning concurrent workload...")

    start_time = time.perf_counter()

    latencies = []

    with ThreadPoolExecutor(
        max_workers=WORKERS
    ) as executor:

        futures = []

        for worker_id in range(WORKERS):

            for operation_id in range(
                OPERATIONS_PER_WORKER
            ):

                future = executor.submit(
                    worker_operation,
                    worker_id,
                    operation_id
                )

                futures.append(future)

        for future in as_completed(futures):

            latency = future.result()

            latencies.append(latency)

    end_time = time.perf_counter()

    total_time = end_time - start_time

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

    average = statistics.mean(latencies)

    minimum = min(latencies)
    maximum = max(latencies)

    throughput = (
        total_operations / total_time
    )

    # --------------------------------------------------
    # Results
    # --------------------------------------------------

    print("\n==========================================")
    print("RESULTS")
    print("==========================================")

    print(
        f"Total operations : "
        f"{total_operations}"
    )

    print(
        f"Total time      : "
        f"{total_time:.3f} seconds"
    )

    print(
        f"Average         : "
        f"{average:.3f} ms"
    )

    print(
        f"p50             : "
        f"{p50:.3f} ms"
    )

    print(
        f"p95             : "
        f"{p95:.3f} ms"
    )

    print(
        f"Minimum         : "
        f"{minimum:.3f} ms"
    )

    print(
        f"Maximum         : "
        f"{maximum:.3f} ms"
    )

    print(
        f"Throughput      : "
        f"{throughput:.2f} operations/sec"
    )


if __name__ == "__main__":
    main()