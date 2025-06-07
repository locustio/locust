# Locust Usage Patterns and Examples

This document provides common usage patterns and examples for the Locust load testing framework. Use it as a quick reference for implementing different testing scenarios.

## Basic HTTP Test

The most common use case for Locust is testing HTTP services:

```python
from locust import HttpUser, task, between

class BasicUser(HttpUser):
    wait_time = between(1, 5)  # Wait 1-5 seconds between tasks
    
    @task
    def index_page(self):
        # Simple GET request to the home page
        self.client.get("/")
    
    @task(3)  # This task is 3x more likely to be executed
    def view_item(self):
        # Using a fixed name helps group requests in the statistics
        item_id = 5
        self.client.get(f"/item?id={item_id}", name="/item")
    
    @task
    def submit_form(self):
        # POST request with JSON payload
        self.client.post("/submit", json={
            "username": "test_user",
            "password": "secret"
        })
        
        # You can also use the data parameter for form data:
        # self.client.post("/submit", data={
        #     "username": "test_user",
        #     "password": "secret"
        # })
```

## User Authentication

Handle user authentication in the `on_start` method:

```python
from locust import HttpUser, task, between

class AuthenticatedUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Login at the start of each user's session
        response = self.client.post("/login", json={
            "username": "test_user",
            "password": "secret"
        })
        
        # Store the session token/cookie for subsequent requests
        self.token = response.json()["token"]
    
    @task
    def protected_resource(self):
        # Use the token in the Authorization header
        self.client.get("/protected-resource", headers={
            "Authorization": f"Bearer {self.token}"
        })
    
    def on_stop(self):
        # Logout at the end of the session
        self.client.post("/logout")
```

## Weighted Tasks

Control the relative frequency of tasks:

```python
from locust import HttpUser, task, between

class WeightedTaskUser(HttpUser):
    wait_time = between(1, 2)
    
    @task(10)  # High frequency
    def index_page(self):
        self.client.get("/")
    
    @task(3)  # Medium frequency
    def product_page(self):
        self.client.get("/products")
    
    @task(1)  # Low frequency
    def checkout(self):
        self.client.post("/checkout")
```

## Task Sets

Group related tasks together:

```python
from locust import HttpUser, TaskSet, task, between

class BrowsingBehavior(TaskSet):
    @task(5)
    def index_page(self):
        self.client.get("/")
    
    @task(2)
    def about_page(self):
        self.client.get("/about")
    
    @task(1)
    def stop(self):
        # Return to the parent TaskSet or User
        self.interrupt()

class PurchaseBehavior(TaskSet):
    @task
    def product_page(self):
        self.client.get("/products")
    
    @task
    def add_to_cart(self):
        self.client.post("/cart/add", json={"product_id": 123})
    
    @task
    def checkout(self):
        self.client.post("/checkout")
        self.interrupt()  # Go back to main user after checkout

class ShopperUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def browsing(self):
        # Spawn BrowsingBehavior task set
        self.schedule_task(BrowsingBehavior)
    
    @task(1)
    def purchasing(self):
        # Spawn PurchaseBehavior task set
        self.schedule_task(PurchaseBehavior)
```

## Sequential Tasks

Execute tasks in a defined sequence:

```python
from locust import HttpUser, SequentialTaskSet, task, between

class CheckoutFlow(SequentialTaskSet):
    @task
    def add_to_cart(self):
        self.client.post("/cart/add", json={"product_id": 123})
    
    @task
    def view_cart(self):
        self.client.get("/cart")
    
    @task
    def enter_shipping_info(self):
        self.client.post("/checkout/shipping", json={
            "address": "123 Test St",
            "city": "Test City",
            "zip": "12345"
        })
    
    @task
    def enter_payment(self):
        self.client.post("/checkout/payment", json={
            "card_number": "4111111111111111",
            "expiry": "12/25",
            "cvv": "123"
        })
    
    @task
    def confirm_order(self):
        self.client.post("/checkout/confirm")
        self.interrupt()  # End the sequence

class ShopperUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def checkout_process(self):
        self.schedule_task(CheckoutFlow)
```

## Dynamic Data

Load test data from external sources:

```python
import random
import csv
from locust import HttpUser, task, between

class DataDrivenUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Load test data from CSV
        with open("test_data.csv") as f:
            reader = csv.reader(f)
            next(reader)  # Skip header row
            self.test_data = list(reader)
    
    @task
    def search_product(self):
        # Randomly select a search term from test data
        if self.test_data:
            row = random.choice(self.test_data)
            search_term = row[0]
            self.client.get(f"/search?q={search_term}")
```

## Custom Load Shape

Define custom load patterns:

```python
from locust import HttpUser, task, between
from locust import LoadTestShape

class StagesShape(LoadTestShape):
    """
    A load test shape that changes user count in stages
    """
    stages = [
        {"duration": 60, "users": 10, "spawn_rate": 10},
        {"duration": 120, "users": 50, "spawn_rate": 10},
        {"duration": 180, "users": 100, "spawn_rate": 10},
        {"duration": 240, "users": 30, "spawn_rate": 10},
        {"duration": 300, "users": 0, "spawn_rate": 10},
    ]

    def tick(self):
        run_time = self.get_run_time()
        
        for stage in self.stages:
            if run_time < stage["duration"]:
                return (stage["users"], stage["spawn_rate"])
        
        return None  # Test is finished

class WebsiteUser(HttpUser):
    wait_time = between(1, 5)
    
    @task
    def index_page(self):
        self.client.get("/")
```

## Custom Metrics

Record custom metrics:

```python
from locust import HttpUser, task, between, events
import time

# Custom setup for tracking metrics
stats = {}

@events.init.add_listener
def on_locust_init(environment, **kwargs):
    global stats
    stats = {
        "cache_hits": 0,
        "cache_misses": 0,
        "business_metric": 0
    }

@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    # Report custom metrics at the end
    print(f"Custom metrics: {stats}")

class CustomMetricsUser(HttpUser):
    wait_time = between(1, 3)
    
    @task
    def get_cached_data(self):
        start_time = time.time()
        response = self.client.get("/api/data")
        
        # Track custom metrics based on response
        if "X-Cache-Hit" in response.headers:
            if response.headers["X-Cache-Hit"] == "1":
                stats["cache_hits"] += 1
            else:
                stats["cache_misses"] += 1
        
        # Track business metrics from response data
        if response.status_code == 200:
            data = response.json()
            if "value" in data and data["value"] > 100:
                stats["business_metric"] += 1
            
            # Report custom timing metric
            processing_time = data.get("processing_time", 0)
            self.environment.events.request_success.fire(
                request_type="Custom",
                name="Backend Processing Time",
                response_time=processing_time,
                response_length=0,
            )
```

## Testing REST APIs

Test RESTful APIs with different HTTP methods:

```python
from locust import HttpUser, task, between
import random

class RestApiUser(HttpUser):
    wait_time = between(1, 3)
    
    def on_start(self):
        # Authenticate and get token
        response = self.client.post("/api/auth", json={
            "username": "api_user",
            "password": "api_pass"
        })
        self.token = response.json()["token"]
        self.headers = {"Authorization": f"Bearer {self.token}"}
        
        # Create some test data to work with
        response = self.client.post("/api/resources", 
                                   json={"name": "Test Resource"},
                                   headers=self.headers)
        self.resource_id = response.json()["id"]
    
    @task(4)
    def get_resource(self):
        # GET - Read operation
        self.client.get(f"/api/resources/{self.resource_id}", 
                       headers=self.headers)
    
    @task(2)
    def list_resources(self):
        # GET with query parameters
        params = {
            "page": random.randint(1, 5),
            "limit": 10,
            "sort": random.choice(["name", "date", "status"])
        }
        self.client.get("/api/resources", params=params, headers=self.headers)
    
    @task(1)
    def update_resource(self):
        # PUT/PATCH - Update operation
        self.client.put(f"/api/resources/{self.resource_id}", 
                       json={"name": f"Updated Resource {random.randint(1, 1000)}"},
                       headers=self.headers)
    
    @task(1)
    def create_secondary_resource(self):
        # POST - Create operation with nested resources
        self.client.post(f"/api/resources/{self.resource_id}/items", 
                        json={"description": f"Item {random.randint(1, 1000)}"},
                        headers=self.headers)
```

## Testing WebSockets

Test WebSocket connections:

```python
import time
import json
import gevent
from locust import HttpUser, task, between, events

class WebSocketClient:
    def __init__(self, host):
        # The websocket-client library needs to be installed separately
        # pip install websocket-client
        import websocket
        self.host = host
        # Use wss:// for secure WebSocket connections
        self.ws = websocket.create_connection(f"ws://{self.host}/ws")
    
    def send(self, message):
        self.ws.send(message)
    
    def receive(self):
        return self.ws.recv()
    
    def close(self):
        self.ws.close()

class WebSocketUser(HttpUser):
    wait_time = between(1, 3)
    abstract = True  # Don't instantiate this class directly
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.ws_client = None
        self.background_task = None
        
    def on_start(self):
        # Create WebSocket connection when user starts
        self.ws_client = WebSocketClient(self.host)
        
        # Start a background greenlet to listen for messages
        self.background_task = gevent.spawn(self.ws_receiver)
    
    def ws_receiver(self):
        while True:
            try:
                message = self.ws_client.receive()
                # Log the received message as a success
                # Use Locust's event system to record metrics
                self.environment.events.request_success.fire(
                    request_type="websocket",
                    name="receive",
                    response_time=0,
                    response_length=len(message)
                )
            except Exception as e:
                # Log any errors
                self.environment.events.request_failure.fire(
                    request_type="websocket",
                    name="receive",
                    response_time=0,
                    exception=e
                )
                break
    
    def on_stop(self):
        # Clean up resources when user stops
        if self.background_task:
            self.background_task.kill()
        if self.ws_client:
            self.ws_client.close()

class ChatUser(WebSocketUser):
    @task
    def send_message(self):
        if self.ws_client:
            start_time = time.time()
            try:
                message = json.dumps({
                    "type": "message",
                    "content": f"Hello from user at {time.time()}"
                })
                self.ws_client.send(message)
                
                # Log the sent message as a success
                self.environment.events.request_success.fire(
                    request_type="websocket",
                    name="send",
                    response_time=(time.time() - start_time) * 1000,
                    response_length=len(message)
                )
            except Exception as e:
                # Log any errors
                self.environment.events.request_failure.fire(
                    request_type="websocket",
                    name="send",
                    response_time=(time.time() - start_time) * 1000,
                    exception=e
                )
```

## Testing GraphQL

Test GraphQL APIs:

```python
from locust import HttpUser, task, between
import random

class GraphQLUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def get_user(self):
        # Simple query
        user_id = random.randint(1, 100)
        query = """
        query GetUser {
            user(id: %d) {
                id
                name
                email
                posts {
                    id
                    title
                }
            }
        }
        """ % user_id
        
        self.client.post("/graphql", 
                        json={"query": query},
                        name="GraphQL: GetUser")
    
    @task(1)
    def create_post(self):
        # Mutation
        mutation = """
        mutation CreatePost {
            createPost(input: {
                title: "Test Post %d",
                content: "This is a test post content"
            }) {
                id
                title
                createdAt
            }
        }
        """ % random.randint(1, 1000)
        
        self.client.post("/graphql", 
                        json={"query": mutation},
                        name="GraphQL: CreatePost")
    
    @task(2)
    def complex_query(self):
        # More complex query with variables
        query = """
        query SearchPosts($searchTerm: String!, $limit: Int!) {
            searchPosts(searchTerm: $searchTerm, limit: $limit) {
                id
                title
                content
                author {
                    id
                    name
                }
                comments {
                    id
                    content
                }
            }
        }
        """
        
        variables = {
            "searchTerm": random.choice(["test", "api", "graphql", "locust"]),
            "limit": random.randint(5, 20)
        }
        
        self.client.post("/graphql", 
                        json={"query": query, "variables": variables},
                        name="GraphQL: SearchPosts")
```

## Testing with Multiple User Types

Simulate different types of users:

```python
from locust import HttpUser, task, between

class BrowserUser(HttpUser):
    weight = 3  # This user type will be 3x more common
    wait_time = between(2, 5)
    
    @task
    def browse_products(self):
        self.client.get("/products")
    
    @task
    def view_product_details(self):
        product_id = random.randint(1, 100)
        self.client.get(f"/products/{product_id}")

class MobileAppUser(HttpUser):
    weight = 2  # This user type will be 2x more common than AdminUser
    wait_time = between(1, 3)
    
    @task
    def api_get_products(self):
        self.client.get("/api/products")
    
    @task
    def api_get_user_profile(self):
        self.client.get("/api/profile")

class AdminUser(HttpUser):
    weight = 1  # Least common user type
    wait_time = between(5, 10)
    
    def on_start(self):
        self.client.post("/admin/login", json={
            "username": "admin",
            "password": "admin_password"
        })
    
    @task
    def admin_dashboard(self):
        self.client.get("/admin/dashboard")
    
    @task
    def manage_products(self):
        self.client.get("/admin/products")
```

## Command Line Usage Examples

Run Locust with different configurations:

```bash
# Basic usage with web UI
locust -f locustfile.py

# Headless mode with 100 users, spawn rate of 10 users/sec, run for 5 minutes
locust -f locustfile.py --headless -u 100 -r 10 -t 5m

# Specify host
locust -f locustfile.py --host=https://example.com

# Distributed mode - master
locust -f locustfile.py --master

# Distributed mode - worker
locust -f locustfile.py --worker --master-host=192.168.0.10

# Export results to CSV
locust -f locustfile.py --headless -u 100 -r 10 -t 5m --csv=results

# Run with specific user classes
locust -f locustfile.py --user-classes MobileAppUser,AdminUser

# Run with HTML report
locust -f locustfile.py --headless -u 100 -r 10 -t 5m --html=report.html
```

## Common Patterns for Result Analysis

Analyze Locust test results:

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load test results from CSV
stats = pd.read_csv("results_stats.csv")
history = pd.read_csv("results_stats_history.csv")

# Print summary statistics
print(stats[["Name", "Request Count", "Failure Count", "Median Response Time", "Average Response Time"]])

# Plot response times over time
plt.figure(figsize=(12, 6))
for name in history["Name"].unique():
    if name != "Aggregated":
        data = history[history["Name"] == name]
        plt.plot(data["Timestamp"], data["Average Response Time"], label=name)

plt.title("Response Time Over Time")
plt.xlabel("Time")
plt.ylabel("Response Time (ms)")
plt.legend()
plt.grid(True)
plt.savefig("response_times.png")

# Plot users and request rate
plt.figure(figsize=(12, 6))
plt.plot(history[history["Name"] == "Aggregated"]["Timestamp"], 
         history[history["Name"] == "Aggregated"]["User Count"],
         label="Users")
plt.plot(history[history["Name"] == "Aggregated"]["Timestamp"], 
         history[history["Name"] == "Aggregated"]["Requests/s"],
         label="Requests/s")
plt.title("Users and Request Rate")
plt.xlabel("Time")
plt.legend()
plt.grid(True)
plt.savefig("users_and_rps.png")
```
