import streamlit as st

st.set_page_config(
    page_title="CognoDB Benchmark",
    page_icon="📊",
    layout="wide"
)

st.title("📊 CognoDB Graph Database Benchmark")
st.subheader("Wiki-Vote Dataset Performance Analysis")

st.markdown("""
This project benchmarks graph database performance using the Wiki-Vote dataset.

### Dataset
- Nodes: **7,115**
- Relationships: **103,689**

### Databases
- CognoDB
- Neo4j
- Memgraph
- FalkorDB
""")

st.divider()

st.header("🚀 Benchmark Results")

data = {
    "Benchmark": [
        "1-Hop Traversal",
        "2-Hop Traversal",
        "3-Hop Traversal",
        "Point Lookup",
        "Indexed Lookup",
        "Aggregation",
        "Mixed Read/Write",
        "Concurrent"
    ],
    "CognoDB": [
        235.520,
        257.266,
        558.909,
        244.417,
        230.830,
        583.110,
        1228.723,
        2425.548
    ],
    "Neo4j": [
        100.394,
        101.881,
        230.207,
        82.917,
        82.274,
        100.404,
        81.850,
        1128.284
    ],
    "Memgraph": [
        242.453,
        255.840,
        532.428,
        242.572,
        241.864,
        277.803,
        247.058,
        None
    ],
    "FalkorDB": [
        None,
        19.222,
        28.798,
        17.278,
        18.291,
        61.114,
        66.235,
        73.820
    ]
}

st.dataframe(data, use_container_width=True)

st.caption("Values shown are p50 latency in milliseconds.")

st.divider()

st.header("📌 Key Findings")

st.success(
    "FalkorDB recorded the lowest p50 latency in the reported "
    "2-hop, 3-hop, point lookup, indexed lookup, aggregation, "
    "mixed read/write and concurrent workloads."
)

st.info(
    "Neo4j also demonstrated substantially lower latency than "
    "CognoDB and Memgraph in the comparable workloads."
)

st.warning(
    "FalkorDB 1-hop and Memgraph concurrent benchmark values "
    "were not available in the recorded results."
)