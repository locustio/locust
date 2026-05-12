"""
REST API with Bearer Token Authentication

This example shows how to authenticate with bearer tokens and use them
for subsequent API calls.

Usage:
    locust -f rest_api_auth_bearer.py --host=http://localhost:8000
"""

from locust import HttpUser, between, task


class BearerTokenUser(HttpUser):
    """Simulates users authenticated with bearer tokens"""

    wait_time = between(1, 3)
    token = None

    def on_start(self):
        """Called when a simulated user starts - authenticate first"""
        response = self.client.post(
            "/api/auth/login",
            json={"username": "testuser", "password": "testpass"}
        )

        if response.status_code == 200:
            data = response.json()
            self.token = data.get("token")
            # Update headers for all subsequent requests
            self.client.headers.update({
                "Authorization": f"Bearer {self.token}"
            })
            print(f"✓ Authenticated with token: {self.token[:20]}...")
        else:
            print(f"✗ Authentication failed: {response.status_code}")
            print(f"  Response: {response.text}")
            self.token = None

    @task(2)
    def list_items(self):
        """List items - requires bearer token"""
        if not self.token:
            return  # Skip if not authenticated

        self.client.get("/api/items", name="/api/items")

    @task(1)
    def get_user_profile(self):
        """Access protected user profile"""
        if not self.token:
            return

        self.client.get("/api/user/profile", name="/api/user/profile")

    @task(1)
    def create_item(self):
        """Create item - requires authentication"""
        if not self.token:
            return

        payload = {"name": "New Item", "price": 50.00}
        self.client.post("/api/items", json=payload, name="/api/items")

    @task(1)
    def update_profile(self):
        """Update user profile"""
        if not self.token:
            return

        payload = {"name": "Updated Name"}
        self.client.put("/api/user/profile", json=payload)


if __name__ == "__main__":
    print("Bearer Token Authentication Example")
    print("Usage: locust -f rest_api_auth_bearer.py --host=http://localhost:8000")
