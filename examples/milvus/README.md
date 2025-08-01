# Milvus Load Testing with Locust

## Overview

This example demonstrates how to perform load testing on Milvus using Locust. It includes a comprehensive test suite that covers all major Milvus operations: insert, upsert, search, query, delete, and hybrid search.

## Prerequisites

- [`pymilvus`](https://github.com/milvus-io/pymilvus)
  - Official Milvus Python SDK (v2.x)


## How to run the test

### Basic Usage

```bash
# Run with Locust web UI
locust -f locustfile.py --host=http://localhost:19530

# Run headless (without web UI)
locust -f locustfile.py --host=http://localhost:19530 --headless --users=5 --spawn-rate=1 --run-time=60s
```

### Custom Parameters

The test supports various custom parameters:

```bash
locust -f locustfile.py \
  --host=http://localhost:19530 \
  --token=root:Milvus \
  --collection-name=load_test_collection \
  --db-name=default \
  --dimension=256 \
  --index-type=HNSW \
  --metric-type=L2 \
  --timeout=30
```



## Notes

- You should choose the specified schema and index for your test
- Ground truth data should be caculated for recall testing
- It is recommended to use the `--processes` parameter for distributed testing
- See [Locust distributed documentation](https://docs.locust.io/en/stable/running-distributed.html) for scaling tests



