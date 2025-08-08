#!/usr/bin/env python3
"""
Simple example demonstrating all Milvus request types using the MilvusUser class.
This is a minimal example that includes: insert, upsert, search, query, and delete operations.
"""

from locust import TaskSet, between, events, task
from locust.contrib.milvus import MilvusUser

import random

import numpy as np
from pymilvus import CollectionSchema, DataType, FieldSchema
from pymilvus.milvus_client import IndexParams

# Global variables to store configuration
milvus_config = {
    "token": "root:Milvus",
    "collection_name": "simple_test_collection",
    "db_name": "default",
    "timeout": 30,
    "dimension": 128,
    "index_type": "IVF_FLAT",
    "metric_type": "L2",
    "params": {},
}


@events.init_command_line_parser.add_listener
def init_parser(parser):
    """Add custom command line arguments."""
    parser.add_argument(
        "--token", type=str, default="root:Milvus", help="Milvus authentication token (default: root:Milvus)"
    )
    parser.add_argument(
        "--collection-name",
        type=str,
        default="simple_test_collection",
        help="Collection name (default: simple_test_collection)",
    )
    parser.add_argument("--db-name", type=str, default="default", help="Database name (default: default)")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout in seconds (default: 30)")
    parser.add_argument("--dimension", type=int, default=128, help="Vector dimension (default: 128)")
    parser.add_argument("--index-type", type=str, default="IVF_FLAT", help="Index type (default: IVF_FLAT)")
    parser.add_argument("--metric-type", type=str, default="L2", help="Metric type (default: L2)")
    parser.add_argument("--params", type=dict, default={}, help="Index parameters (default: {})")


@events.init.add_listener
def on_init(environment, **kwargs):
    """Update configuration from parsed arguments."""
    if environment.parsed_options:
        milvus_config["token"] = environment.parsed_options.token
        milvus_config["collection_name"] = environment.parsed_options.collection_name
        milvus_config["db_name"] = environment.parsed_options.db_name
        milvus_config["timeout"] = environment.parsed_options.timeout
        milvus_config["dimension"] = environment.parsed_options.dimension
        milvus_config["index_type"] = environment.parsed_options.index_type
        milvus_config["metric_type"] = environment.parsed_options.metric_type
        milvus_config["params"] = environment.parsed_options.params


class SimpleMilvusTaskSet(TaskSet):
    """Simple TaskSet demonstrating all Milvus operations."""

    user: MilvusUser

    def on_start(self):
        """Initialize test data."""
        self.dimension = milvus_config["dimension"]
        self.inserted_ids = []

        # Pre-generate some test vectors
        self.test_vectors = [np.random.random(self.dimension).astype(np.float32).tolist() for _ in range(10)]

        # Insert some initial data
        self._insert_initial_data()

    def _insert_initial_data(self):
        """Insert a few records to enable query and delete operations."""
        data = [
            {
                "id": i,
                "vector": self.test_vectors[i % len(self.test_vectors)],
                "name": f"item_{i}",
                "category": random.choice(["A", "B", "C"]),
            }
            for i in range(1, 11)
        ]

        result = self.user.insert(data)
        if result["success"]:
            self.inserted_ids = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @task(3)
    def insert_data(self):
        """Insert new data into Milvus."""
        new_id = random.randint(1000, 9999)
        data = [
            {
                "id": new_id,
                "vector": random.choice(self.test_vectors),
                "name": f"item_{new_id}",
                "category": random.choice(["A", "B", "C"]),
            }
        ]

        result = self.user.insert(data)
        if result["success"]:
            self.inserted_ids.append(new_id)

    @task(2)
    def upsert_data(self):
        """Update existing data or insert new data."""
        if self.inserted_ids:
            # Update existing record
            update_id = random.choice(self.inserted_ids)
            data = [
                {
                    "id": update_id,
                    "vector": random.choice(self.test_vectors),
                    "name": f"updated_item_{update_id}",
                    "category": random.choice(["X", "Y", "Z"]),
                }
            ]
        else:
            # Insert new record
            new_id = random.randint(5000, 5999)
            data = [
                {
                    "id": new_id,
                    "vector": random.choice(self.test_vectors),
                    "name": f"new_item_{new_id}",
                    "category": random.choice(["A", "B", "C"]),
                }
            ]
            self.inserted_ids.append(new_id)

        self.user.upsert(data)

    @task(5)
    def search_vectors(self):
        """Search for similar vectors."""
        search_vector = random.choice(self.test_vectors)

        self.user.search(data=[search_vector], anns_field="vector", limit=5, output_fields=["id", "name", "category"])

    @task(3)
    def search_with_filter(self):
        """Search with a filter condition."""
        search_vector = random.choice(self.test_vectors)
        category = random.choice(["A", "B", "C"])

        self.user.search(
            data=[search_vector],
            anns_field="vector",
            limit=5,
            filter=f'category == "{category}"',
            output_fields=["id", "name", "category"],
        )

    @task(4)
    def query_by_id(self):
        """Query specific records by ID."""
        if self.inserted_ids:
            query_id = random.choice(self.inserted_ids)

            self.user.query(filter=f"id == {query_id}", output_fields=["id", "name", "category"])

    @task(3)
    def query_by_category(self):
        """Query records by category."""
        category = random.choice(["A", "B", "C", "X", "Y", "Z"])

        self.user.query(filter=f'category == "{category}"', output_fields=["id", "name", "category"])

    @task(2)
    def search_with_recall(self):
        """Search with recall calculation."""
        search_vector = random.choice(self.test_vectors)

        # For this example, we'll use the first 5 inserted IDs as ground truth
        # In real scenarios, ground truth would be pre-computed based on actual relevance
        ground_truth = self.inserted_ids[:5] if len(self.inserted_ids) >= 5 else self.inserted_ids

        self.user.search(
            data=[search_vector],
            anns_field="vector",
            limit=5,
            output_fields=["id", "name", "category"],
            calculate_recall=True,
            ground_truth=ground_truth,
        )

    @task(1)
    def delete_data(self):
        """Delete records from Milvus."""
        if len(self.inserted_ids) > 10:
            delete_id = random.choice(self.inserted_ids)

            result = self.user.delete(filter=f"id == {delete_id}")
            if result["success"]:
                self.inserted_ids.remove(delete_id)


class SimpleMilvusUser(MilvusUser):
    """Simple Milvus user for demonstrating all operations."""

    tasks = [SimpleMilvusTaskSet]
    wait_time = between(0.5, 2)

    def __init__(self, environment):
        # Define collection schema
        schema = CollectionSchema(
            fields=[
                FieldSchema(name="id", dtype=DataType.INT64, is_primary=True),
                FieldSchema(name="vector", dtype=DataType.FLOAT_VECTOR, dim=milvus_config["dimension"]),
                FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=50),
                FieldSchema(name="category", dtype=DataType.VARCHAR, max_length=10),
            ],
            description="Simple test collection",
            auto_id=False,
        )

        # Define index parameters
        index_params = IndexParams()
        index_params.add_index(
            field_name="vector",
            index_type=milvus_config["index_type"],
            metric_type=milvus_config["metric_type"],
            params=milvus_config["params"],
        )

        # Initialize MilvusUser
        # Use host from locust's --host parameter
        super().__init__(
            environment,
            uri=environment.host,  # Use --host parameter from locust
            token=milvus_config["token"],
            collection_name=milvus_config["collection_name"],
            db_name=milvus_config["db_name"],
            timeout=milvus_config["timeout"],
            schema=schema,
            index_params=index_params,
        )


if __name__ == "__main__":
    print("Simple Milvus Test Example")
    print("==========================")
    print("\nThis example demonstrates all Milvus request types:")
    print("- Insert: Add new records")
    print("- Upsert: Update existing or insert new records")
    print("- Search: Find similar vectors")
    print("- Search with filter: Find similar vectors with conditions")
    print("- Search with recall: Search with recall calculation")
    print("- Query by ID: Retrieve specific records")
    print("- Query by category: Retrieve records by scalar field")
    print("- Delete: Remove records")

    print("\nUsage:")
    print("locust -f locustfile.py --host=http://localhost:19530")
    print("\nOr run headless:")
    print("locust -f locustfile.py --host=http://localhost:19530 --headless --users=5 --spawn-rate=1 --run-time=60s")

    print("\nCustom parameters:")
    print("--token: Authentication token (default: root:Milvus)")
    print("--collection-name: Collection name (default: simple_test_collection)")
    print("--db-name: Database name (default: default)")
    print("--timeout: Request timeout in seconds (default: 30)")
    print("--dimension: Vector dimension (default: 128)")
    print("--index-type: Index type (default: IVF_FLAT)")
    print("--metric-type: Metric type (default: L2)")
    print("--nlist: Number of cluster units (default: 128)")

    print("\nExample with custom parameters:")
    print(
        "locust -f locustfile.py --host=http://milvus-server:19530 --token=user:password --collection-name=my_collection --dimension=256"
    )

    print("\nTask weights (relative frequency):")
    print("- Search: 5")
    print("- Query by ID: 4")
    print("- Insert: 3")
    print("- Search with filter: 3")
    print("- Query by category: 3")
    print("- Search with recall: 2")
    print("- Upsert: 2")
    print("- Delete: 1")
