# Milvus Load Testing with Locust

Simple example demonstrating load testing for Milvus vector database operations.

## Prerequisites

Install Locust with Milvus support:

```bash
# Using pip
pip install locust[milvus]

# Using uv
uv add locust[milvus]
# or
uv sync --extra milvus
```

This installs the required dependencies:
- [`pymilvus`](https://github.com/milvus-io/pymilvus) - Official Milvus Python SDK (>=2.5.0)

## Usage

```bash
# Run with web UI
locust -f locustfile.py --host=http://localhost:19530

# Run headless
locust -f locustfile.py --host=http://localhost:19530 --headless --users=10 --spawn-rate=2 --run-time=60s
```

## Operations Tested

- Insert vectors
- Search vectors  
- Query by filter
- Delete records

For more advanced usage, see the [Locust documentation](https://docs.locust.io/).



