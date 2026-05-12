"""
REST API with Error Handling and Validation

This example demonstrates proper error handling, response validation,
and custom error reporting.

Usage:
    locust -f rest_api_with_validation.py --host=http://localhost:8000
"""

from locust import HttpUser, between, task

import json


class ErrorHandlingUser(HttpUser):
    """Simulates users with proper error handling"""

    wait_time = between(1, 3)

    @task(2)
    def list_items_with_validation(self):
        """List items with response validation"""
        with self.client.get("/api/items", catch_response=True) as response:
            if response.status_code == 200:
                try:
                    data = response.json()
                    if isinstance(data, list):
                        response.success()
                    else:
                        response.failure("Expected list response, got " + str(type(data)))
                except json.JSONDecodeError:
                    response.failure("Invalid JSON in response")
            else:
                response.failure(f"Expected 200, got {response.status_code}")

    @task(1)
    def create_item_with_validation(self):
        """Create item with error handling"""
        payload = {"name": "Test Item", "price": 99.99}

        with self.client.post(
            "/api/items",
            json=payload,
            catch_response=True
        ) as response:
            if response.status_code == 201:
                response.success()
            elif response.status_code == 400:
                response.failure(f"Invalid request: {response.text}")
            elif response.status_code == 500:
                response.failure("Server error")
            else:
                response.failure(f"Unexpected status: {response.status_code}")

    @task(1)
    def get_item_with_fallback(self):
        """Get item with fallback on error"""
        response = self.client.get("/api/items/42", catch_response=True)

        if response.status_code == 200:
            response.success()
        elif response.status_code == 404:
            # 404 is expected for non-existent items
            response.success()
        else:
            response.failure(f"Unexpected error: {response.status_code}")

    @task(1)
    def delete_item_safe(self):
        """Delete item safely"""
        with self.client.delete("/api/items/999", catch_response=True) as response:
            # Accept both 204 (deleted) and 404 (not found)
            if response.status_code in [204, 404]:
                response.success()
            else:
                response.failure(f"Delete failed: {response.status_code}")


if __name__ == "__main__":
    print("Error Handling Example")
    print("Usage: locust -f rest_api_with_validation.py --host=http://localhost:8000")
