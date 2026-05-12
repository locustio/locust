"""
Basic REST API Load Testing Example

This example demonstrates how to test a typical REST API with multiple
endpoints and task weights.

Usage:
    locust -f rest_api_basic.py --host=http://localhost:8000
"""

from locust import HttpUser, between, task


class RestApiUser(HttpUser):
    """Simulates a user interacting with a REST API"""

    wait_time = between(1, 3)  # Wait 1-3 seconds between requests

    @task(2)
    def list_items(self):
        """
        Fetch list of items
        Weight of 2 means this runs twice as often as @task(1) methods
        """
        self.client.get("/api/items", name="/api/items")

    @task(1)
    def get_item_detail(self):
        """Fetch a single item by ID"""
        # In real scenarios, you'd vary the ID
        self.client.get("/api/items/42", name="/api/items/[id]")

    @task(1)
    def create_item(self):
        """Create a new item"""
        payload = {
            "name": "Test Item",
            "description": "A test item",
            "price": 99.99
        }
        self.client.post("/api/items", json=payload, name="/api/items")

    @task(1)
    def update_item(self):
        """Update an existing item"""
        payload = {
            "name": "Updated Item",
            "price": 89.99
        }
        self.client.put("/api/items/42", json=payload, name="/api/items/[id]")

    @task(1)
    def delete_item(self):
        """Delete an item"""
        self.client.delete("/api/items/42", name="/api/items/[id]")


if __name__ == "__main__":
    print("Usage: locust -f rest_api_basic.py --host=http://target-url")
    print("\nExample:")
    print("  locust -f rest_api_basic.py --host=http://localhost:8000 -u 100 -c 10")
