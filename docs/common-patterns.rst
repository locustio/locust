.. _common-patterns:

====================
Common Load Patterns
====================

This guide covers common patterns and best practices for load testing different types of APIs and systems with Locust. Each section includes runnable examples you can adapt to your specific use case.

.. contents::
   :local:

.. _rest-api-patterns:

REST API Load Testing
=====================

The most common use case for Locust is testing REST APIs. This section covers various patterns for testing typical REST endpoints.

Basic REST API Pattern
----------------------

Here's a simple pattern for testing a typical REST API with multiple endpoints:

.. code-block:: python

    from locust import HttpUser, task, between, events
    from urllib.parse import urljoin

    class RestApiUser(HttpUser):
        wait_time = between(1, 3)

        def on_start(self):
            """Called when a simulated user starts"""
            # Get API base URL from host parameter
            self.api_url = self.client.base_url

        @task(2)
        def list_items(self):
            """Fetch list of items - weight 2 (runs twice as often)"""
            response = self.client.get(
                "/api/items",
                name="/api/items"
            )

        @task(1)
        def get_item_detail(self):
            """Fetch a single item by ID"""
            item_id = 42  # In real scenarios, vary this
            response = self.client.get(
                f"/api/items/{item_id}",
                name="/api/items/[id]"
            )

        @task(1)
        def create_item(self):
            """Create a new item"""
            payload = {
                "name": "Test Item",
                "description": "Load test item",
                "price": 99.99
            }
            response = self.client.post(
                "/api/items",
                json=payload,
                name="/api/items"
            )

    if __name__ == "__main__":
        # Run with: locust -f this_file.py --host=http://localhost:8000
        pass


REST API with Bearer Token Authentication
------------------------------------------

Many APIs require bearer token authentication. Here's how to handle it:

.. code-block:: python

    from locust import HttpUser, task, between
    import json

    class AuthenticatedRestUser(HttpUser):
        wait_time = between(1, 3)
        token = None

        def on_start(self):
            """Login and get bearer token"""
            response = self.client.post(
                "/api/auth/login",
                json={
                    "username": "testuser",
                    "password": "testpass"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                # Set auth header for all subsequent requests
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
            else:
                self.token = None

        @task
        def list_items(self):
            """List items - requires bearer token"""
            if not self.token:
                return  # Skip if not authenticated
            
            response = self.client.get("/api/items")

        @task
        def get_protected_resource(self):
            """Access protected resource"""
            if not self.token:
                return
            
            response = self.client.get(
                "/api/user/profile",
                name="/api/user/profile"
            )


REST API with API Key Authentication
-------------------------------------

API key authentication is common for service-to-service calls:

.. code-block:: python

    from locust import HttpUser, task, between

    class ApiKeyUser(HttpUser):
        wait_time = between(1, 3)
        api_key = "your-api-key-here"  # Or load from environment

        def on_start(self):
            """Set API key for all requests"""
            self.client.headers.update({
                "X-API-Key": self.api_key
            })

        @task
        def get_data(self):
            """Fetch data with API key"""
            response = self.client.get(
                "/api/data",
                headers={"X-API-Key": self.api_key}
            )

        @task
        def create_record(self):
            """Create record with API key"""
            response = self.client.post(
                "/api/records",
                json={"name": "Test"},
                headers={"X-API-Key": self.api_key}
            )


REST API with Error Handling
-----------------------------

Proper error handling helps identify issues in your API:

.. code-block:: python

    from locust import HttpUser, task, between

    class ErrorHandlingUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def api_call_with_validation(self):
            """Make API call and validate response"""
            response = self.client.get("/api/items")
            
            # Check response status
            if response.status_code != 200:
                response.failure(f"Expected 200, got {response.status_code}")
            else:
                try:
                    data = response.json()
                    if not isinstance(data, list):
                        response.failure("Expected list response")
                except json.JSONDecodeError:
                    response.failure("Invalid JSON in response")

        @task
        def post_with_catch_response(self):
            """Use catch_response for fine-grained control"""
            with self.client.post(
                "/api/items",
                json={"name": "Test"},
                catch_response=True
            ) as response:
                if response.status_code == 201:
                    response.success()
                else:
                    response.failure(f"Unexpected status: {response.status_code}")


REST API with Pagination
------------------------

Many APIs use pagination. Here's how to handle it:

.. code-block:: python

    from locust import HttpUser, task, between

    class PaginatedApiUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def fetch_paginated_data(self):
            """Fetch multiple pages of data"""
            page = 1
            items_collected = 0
            
            while items_collected < 100:  # Fetch until we have 100 items
                response = self.client.get(
                    f"/api/items?page={page}&limit=20",
                    name="/api/items"
                )
                
                if response.status_code != 200:
                    break
                
                data = response.json()
                items = data.get("items", [])
                items_collected += len(items)
                
                if len(items) == 0:
                    break  # No more items
                
                page += 1


REST API with Custom Metrics
-----------------------------

Track custom metrics during load testing:

.. code-block:: python

    from locust import HttpUser, task, between, events
    import time

    class MetricsUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def track_response_time(self):
            """Track custom response time metrics"""
            start = time.time()
            response = self.client.get("/api/items")
            elapsed = time.time() - start
            
            if response.status_code == 200:
                # Custom metrics can be accessed via events
                events.request.fire(
                    request_type="http",
                    name="/api/items",
                    response_time=elapsed,
                    response_length=len(response.content),
                    exception=None,
                    context={}
                )


.. _websocket-patterns:

WebSocket Load Testing
======================

Testing WebSocket connections requires a different approach than HTTP.

Basic WebSocket Pattern
-----------------------

.. code-block:: python

    from locust import User, task, between, events
    from locust.contrib.fasthttp import FastHttpUser
    import websocket
    import json
    import threading

    class WebSocketUser(User):
        wait_time = between(1, 3)
        ws = None

        def on_start(self):
            """Connect to WebSocket"""
            try:
                self.ws = websocket.WebSocket()
                self.ws.connect("ws://localhost:8000/ws")
                # Start listener thread
                threading.Thread(target=self.listen_messages, daemon=True).start()
            except Exception as e:
                events.request.fire(
                    request_type="websocket",
                    name="connect",
                    response_time=0,
                    response_length=0,
                    exception=e,
                    context={}
                )

        def listen_messages(self):
            """Listen for WebSocket messages"""
            while self.ws and self.ws.connected:
                try:
                    message = self.ws.recv()
                    if message:
                        events.request.fire(
                            request_type="websocket",
                            name="receive",
                            response_time=0,
                            response_length=len(message),
                            exception=None,
                            context={}
                        )
                except Exception as e:
                    break

        @task
        def send_message(self):
            """Send WebSocket message"""
            try:
                if self.ws and self.ws.connected:
                    payload = json.dumps({"msg": "test", "timestamp": 123456})
                    self.ws.send(payload)
                    events.request.fire(
                        request_type="websocket",
                        name="send",
                        response_time=0,
                        response_length=len(payload),
                        exception=None,
                        context={}
                    )
            except Exception as e:
                events.request.fire(
                    request_type="websocket",
                    name="send",
                    response_time=0,
                    response_length=0,
                    exception=e,
                    context={}
                )

        def on_stop(self):
            """Clean up WebSocket connection"""
            if self.ws:
                self.ws.close()


.. _graphql-patterns:

GraphQL Load Testing
====================

Testing GraphQL APIs with different query types.

Basic GraphQL Query Pattern
---------------------------

.. code-block:: python

    from locust import HttpUser, task, between

    class GraphQLUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def query_items(self):
            """Execute a GraphQL query"""
            query = """
            query {
                items {
                    id
                    name
                    price
                }
            }
            """
            response = self.client.post(
                "/graphql",
                json={"query": query},
                name="query_items"
            )

        @task
        def mutation_create_item(self):
            """Execute a GraphQL mutation"""
            mutation = """
            mutation {
                createItem(input: {name: "Test", price: 99.99}) {
                    id
                    name
                }
            }
            """
            response = self.client.post(
                "/graphql",
                json={"query": mutation},
                name="mutation_create_item"
            )

        @task
        def query_with_variables(self):
            """Execute query with variables"""
            query = """
            query GetItem($id: ID!) {
                item(id: $id) {
                    id
                    name
                    price
                }
            }
            """
            response = self.client.post(
                "/graphql",
                json={
                    "query": query,
                    "variables": {"id": "42"}
                },
                name="query_with_variables"
            )


.. _database-patterns:

Database Stress Testing
=======================

Testing databases directly or through database APIs.

Database Connection Pattern
----------------------------

.. code-block:: python

    from locust import User, task, between, events
    import psycopg2
    from contextlib import contextmanager
    import time

    class DatabaseUser(User):
        wait_time = between(1, 3)

        def on_start(self):
            """Connect to database"""
            try:
                self.conn = psycopg2.connect(
                    host="localhost",
                    database="testdb",
                    user="testuser",
                    password="testpass"
                )
            except Exception as e:
                self.conn = None

        @task
        def query_database(self):
            """Execute a SELECT query"""
            if not self.conn:
                return
            
            cursor = self.conn.cursor()
            start = time.time()
            
            try:
                cursor.execute("SELECT * FROM items LIMIT 10")
                results = cursor.fetchall()
                elapsed = time.time() - start
                
                events.request.fire(
                    request_type="database",
                    name="select_items",
                    response_time=elapsed,
                    response_length=len(results),
                    exception=None,
                    context={}
                )
            except Exception as e:
                elapsed = time.time() - start
                events.request.fire(
                    request_type="database",
                    name="select_items",
                    response_time=elapsed,
                    response_length=0,
                    exception=e,
                    context={}
                )
            finally:
                cursor.close()

        @task
        def insert_data(self):
            """Insert test data"""
            if not self.conn:
                return
            
            cursor = self.conn.cursor()
            start = time.time()
            
            try:
                cursor.execute(
                    "INSERT INTO items (name, price) VALUES (%s, %s)",
                    ("Test Item", 99.99)
                )
                self.conn.commit()
                elapsed = time.time() - start
                
                events.request.fire(
                    request_type="database",
                    name="insert_item",
                    response_time=elapsed,
                    response_length=0,
                    exception=None,
                    context={}
                )
            except Exception as e:
                self.conn.rollback()
                elapsed = time.time() - start
                events.request.fire(
                    request_type="database",
                    name="insert_item",
                    response_time=elapsed,
                    response_length=0,
                    exception=e,
                    context={}
                )
            finally:
                cursor.close()

        def on_stop(self):
            """Close database connection"""
            if self.conn:
                self.conn.close()


.. _file-operations-patterns:

File Upload/Download Testing
=============================

Testing file operations is important for many applications.

File Upload Pattern
-------------------

.. code-block:: python

    from locust import HttpUser, task, between
    from io import BytesIO

    class FileUploadUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def upload_file(self):
            """Upload a file"""
            # Create a test file in memory
            file_content = b"This is test file content" * 100
            files = {"file": ("test.txt", BytesIO(file_content))}
            
            response = self.client.post(
                "/api/upload",
                files=files,
                name="/api/upload"
            )

        @task
        def upload_multipart(self):
            """Upload multiple files"""
            files = {
                "file1": ("test1.txt", BytesIO(b"Content 1")),
                "file2": ("test2.txt", BytesIO(b"Content 2"))
            }
            
            response = self.client.post(
                "/api/upload-multiple",
                files=files,
                name="/api/upload-multiple"
            )


File Download Pattern
---------------------

.. code-block:: python

    from locust import HttpUser, task, between

    class FileDownloadUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def download_file(self):
            """Download a file"""
            response = self.client.get(
                "/api/download/file.pdf",
                name="/api/download"
            )
            
            # Verify we got content
            if len(response.content) == 0:
                response.failure("No content in response")

        @task
        def stream_large_file(self):
            """Download large file efficiently"""
            response = self.client.get(
                "/api/download/large.zip",
                name="/api/download",
                stream=True  # Stream the response
            )
            
            # Read in chunks to avoid loading entire file in memory
            total_size = 0
            for chunk in response.iter_content(chunk_size=8192):
                total_size += len(chunk)


.. _authentication-patterns:

Authentication Patterns
=======================

Common authentication flows used in modern applications.

Session-Based Authentication
-----------------------------

.. code-block:: python

    from locust import HttpUser, task, between

    class SessionAuthUser(HttpUser):
        wait_time = between(1, 3)

        def on_start(self):
            """Login to establish session"""
            response = self.client.post(
                "/login",
                data={
                    "username": "testuser",
                    "password": "testpass"
                }
            )
            # Cookies are automatically maintained by Locust

        @task
        def access_protected_page(self):
            """Access page that requires session"""
            response = self.client.get("/dashboard")


OAuth2 Authentication
---------------------

.. code-block:: python

    from locust import HttpUser, task, between
    import requests

    class OAuth2User(HttpUser):
        wait_time = between(1, 3)
        token = None

        def on_start(self):
            """Get OAuth2 token"""
            # This typically runs once per user
            response = self.client.post(
                "/oauth/token",
                data={
                    "grant_type": "client_credentials",
                    "client_id": "your-client-id",
                    "client_secret": "your-client-secret"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("access_token")
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })

        @task
        def api_call(self):
            """Make API call with OAuth2 token"""
            if self.token:
                response = self.client.get("/api/protected")


JWT Authentication
------------------

.. code-block:: python

    from locust import HttpUser, task, between
    import jwt
    import json

    class JWTUser(HttpUser):
        wait_time = between(1, 3)
        token = None
        secret = "your-secret-key"

        def on_start(self):
            """Get JWT token"""
            response = self.client.post(
                "/auth/login",
                json={
                    "username": "testuser",
                    "password": "testpass"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.token = data.get("token")
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })

        @task
        def access_protected_resource(self):
            """Access API with JWT"""
            if self.token:
                response = self.client.get("/api/profile")


Multi-Step Authentication Flow
-------------------------------

.. code-block:: python

    from locust import HttpUser, task, between

    class MultiStepAuthUser(HttpUser):
        wait_time = between(1, 3)
        access_token = None
        refresh_token = None

        def on_start(self):
            """Initial login"""
            response = self.client.post(
                "/auth/login",
                json={
                    "username": "testuser",
                    "password": "testpass"
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.refresh_token = data.get("refresh_token")
                self._set_auth_header()

        def _set_auth_header(self):
            """Update Authorization header"""
            if self.access_token:
                self.client.headers.update({
                    "Authorization": f"Bearer {self.access_token}"
                })

        def _refresh_token_if_needed(self):
            """Refresh token if expired"""
            response = self.client.post(
                "/auth/refresh",
                json={"refresh_token": self.refresh_token}
            )
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self._set_auth_header()

        @task
        def api_call(self):
            """Make API call, refresh if needed"""
            response = self.client.get("/api/protected")
            
            if response.status_code == 401:
                # Token expired, refresh it
                self._refresh_token_if_needed()
                # Retry the request
                response = self.client.get("/api/protected")


.. _complex-flow-patterns:

Complex User Flow Patterns
===========================

Multi-step scenarios that simulate real user workflows.

User Signup → Browse → Purchase → Logout
-----------------------------------------

.. code-block:: python

    from locust import HttpUser, task, between, TaskSet
    import random

    class SignupAndPurchaseUser(HttpUser):
        wait_time = between(1, 3)
        user_id = None
        items = []

        def on_start(self):
            """Create new account"""
            username = f"testuser_{random.randint(1000, 9999)}"
            response = self.client.post(
                "/api/auth/signup",
                json={
                    "username": username,
                    "email": f"{username}@example.com",
                    "password": "password123"
                }
            )
            
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("id")

        @task(1)
        def browse_items(self):
            """Browse available items"""
            response = self.client.get(
                "/api/items",
                name="/api/items"
            )
            
            if response.status_code == 200:
                self.items = response.json()

        @task(2)
        def view_item_details(self):
            """View item details"""
            if self.items:
                item = random.choice(self.items)
                item_id = item.get("id")
                response = self.client.get(
                    f"/api/items/{item_id}",
                    name="/api/items/[id]"
                )

        @task(1)
        def add_to_cart(self):
            """Add item to cart"""
            if self.items:
                item = random.choice(self.items)
                response = self.client.post(
                    "/api/cart",
                    json={
                        "item_id": item.get("id"),
                        "quantity": random.randint(1, 5)
                    }
                )

        @task(1)
        def checkout(self):
            """Complete purchase"""
            response = self.client.post(
                "/api/checkout",
                json={
                    "payment_method": "credit_card",
                    "shipping_address": "123 Main St"
                }
            )

        def on_stop(self):
            """Cleanup"""
            self.client.post("/api/auth/logout")


State-Machine Based User Behavior
----------------------------------

.. code-block:: python

    from locust import HttpUser, task, between, TaskSet
    import random

    class AuthenticatedTaskSet(TaskSet):
        """Tasks for authenticated users"""
        
        @task
        def view_dashboard(self):
            self.client.get("/dashboard")
        
        @task
        def update_profile(self):
            self.client.put(
                "/api/profile",
                json={"name": "Updated Name"}
            )
        
        @task
        def logout_task(self):
            self.client.post("/logout")
            self.user.state = "logged_out"

    class UnauthenticatedTaskSet(TaskSet):
        """Tasks for unauthenticated users"""
        
        @task
        def view_homepage(self):
            self.client.get("/")
        
        @task
        def login_task(self):
            response = self.client.post(
                "/login",
                data={
                    "username": "testuser",
                    "password": "testpass"
                }
            )
            if response.status_code == 200:
                self.user.state = "logged_in"

    class StateBasedUser(HttpUser):
        """User with state-based behavior"""
        wait_time = between(1, 3)
        state = "logged_out"

        def on_start(self):
            self.state = "logged_out"

        @task
        def choose_task_set(self):
            if self.state == "logged_in":
                self.tasks = [AuthenticatedTaskSet]
            else:
                self.tasks = [UnauthenticatedTaskSet]


Tips and Best Practices
=======================

1. **Use Task Weights**: Use `@task(weight)` to set the probability of tasks running
2. **Name Your Requests**: Always use the `name` parameter for consistent request grouping
3. **Handle Errors Gracefully**: Use `catch_response=True` for fine-grained error handling
4. **Vary Your Load**: Use different wait times to simulate realistic user behavior
5. **Consider Data Variance**: Use random values for IDs, names, etc. to avoid caching effects
6. **Monitor Memory**: Watch for memory leaks in long-running tests
7. **Test Early**: Start testing in development, not just production-like environments

See Also
========

* :ref:`increase-performance` - Performance optimization tips
* :ref:`running-distributed` - Running distributed load tests
* :ref:`writing-a-locustfile` - Writing locustfiles
