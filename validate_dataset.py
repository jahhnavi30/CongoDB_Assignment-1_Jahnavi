from pathlib import Path


DATASET_PATH = Path("data/dataset/Wiki-Vote.txt")

EXPECTED_NODES = 7115
EXPECTED_EDGES = 103689


def validate_dataset():
    nodes = set()
    edges = []

    with DATASET_PATH.open("r", encoding="utf-8") as file:
        for line in file:

            # Ignore comments and empty lines
            if line.startswith("#") or not line.strip():
                continue

            source, target = map(int, line.split())

            nodes.add(source)
            nodes.add(target)

            edges.append((source, target))

    unique_edges = set(edges)

    print("========== DATASET VALIDATION ==========")
    print(f"Dataset file       : {DATASET_PATH}")
    print(f"Unique nodes       : {len(nodes)}")
    print(f"Total edges        : {len(edges)}")
    print(f"Unique edges       : {len(unique_edges)}")
    print(f"Duplicate edges    : {len(edges) - len(unique_edges)}")

    print("\n========== EXPECTED VALUES ==========")
    print(f"Expected nodes     : {EXPECTED_NODES}")
    print(f"Expected edges     : {EXPECTED_EDGES}")

    print("\n========== VALIDATION ==========")

    if len(edges) == EXPECTED_EDGES:
        print("✅ Edge count matches")
    else:
        print("❌ Edge count does NOT match")

    if len(nodes) == EXPECTED_NODES:
        print("✅ Node count matches")
    else:
        print("⚠️ Node count differs from header")

    if len(edges) == len(unique_edges):
        print("✅ No duplicate edges found")
    else:
        print("⚠️ Duplicate edges found")


if __name__ == "__main__":
    validate_dataset()
    