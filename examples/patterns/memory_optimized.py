"""
Memory-Optimized Load Test

This example demonstrates best practices for memory-efficient load testing.

Usage:
    locust -f memory_optimized.py --host=http://localhost:8000
"""

from locust import between, task
from locust.contrib.fasthttp import FastHttpUser

from collections import deque


class MemoryOptimizedUser(FastHttpUser):
    """
    Demonstrates memory optimization techniques:
    1. Uses FastHttpUser instead of HttpUser (30-50% less memory)
    2. Uses bounded deque instead of unbounded list
    3. Avoids storing large responses
    4. Streams large files instead of loading into memory
    """

    wait_time = between(1, 3)

    # Bounded storage - max 100 items
    request_history = deque(maxlen=100)

    @task(2)
    def list_items(self):
        """Fetch and process items efficiently"""
        response = self.client.get("/api/items")

        # Only store essential info, not full response
        if response.status_code == 200:
            # Don't store response object, just track the event
            self.request_history.append({
                "url": response.url,
                "status": response.status_code,
                "size": len(response.content)
            })
            # Automatically drops oldest items when max is reached

    @task(1)
    def get_item_without_storing(self):
        """Access endpoint without storing response"""
        response = self.client.get("/api/items/42")
        # Just check status, don't store response
        if response.status_code == 200:
            pass  # Process in-place, don't keep reference

    @task(1)
    def download_large_file(self):
        """Stream large file instead of loading into memory"""
        with self.client.get("/api/files/data.csv", stream=True) as response:
            if response.status_code == 200:
                # Process file in chunks
                total_size = 0
                for chunk in response.iter_content(chunk_size=8192):
                    total_size += len(chunk)
                    # Process chunk here, then discard
                # Memory stays constant regardless of file size

    @task(1)
    def upload_file(self):
        """Upload file without storing response"""
        # Create file data efficiently
        file_content = b"test data" * 100

        files = {"file": ("test.txt", file_content)}
        response = self.client.post("/api/upload", files=files)
        # Don't store response


if __name__ == "__main__":
    print("Memory-Optimized Load Test Example")
    print("Usage: locust -f memory_optimized.py --host=http://localhost:8000")
    print("\nMemory Efficiency Tips:")
    print("1. Use FastHttpUser instead of HttpUser")
    print("2. Use bounded collections (deque with maxlen)")
    print("3. Don't store large responses")
    print("4. Stream large files instead of loading")
    print("5. Process and discard data immediately")
