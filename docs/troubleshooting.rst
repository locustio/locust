.. _troubleshooting:

===============================
Troubleshooting Load Tests
===============================

This guide helps diagnose and fix common issues when running Locust load tests.

.. contents::
   :local:

Diagnostic Workflow
===================

When something goes wrong during a load test, follow this workflow:

1. **Check Status Code Distribution** - Are requests succeeding?
2. **Monitor Response Times** - Are they acceptable?
3. **Watch Memory Usage** - Is it growing unexpectedly?
4. **Check CPU Usage** - Is it maxed out?
5. **Review Logs** - Are there error messages?
6. **Reproduce Locally** - Can you recreate the issue?

Common Errors and Solutions
============================

.. _error-connection-errors:

Connection Errors
-----------------

**Symptoms:**
- Error: `Connection refused`
- Error: `Connection reset by peer`
- Error: `Temporary failure in name resolution`

**Possible Causes:**
1. Target system is down or unreachable
2. Wrong target URL or port
3. Network connectivity issue
4. Firewall blocking requests

**Solutions:**

.. code-block:: python

    from locust import HttpUser, task, between, events

    class DiagnosticUser(HttpUser):
        wait_time = between(1, 3)

        def on_start(self):
            """Test connectivity on startup"""
            try:
                response = self.client.get("/", timeout=5)
                print(f"✓ Connected to {self.client.base_url}")
            except Exception as e:
                print(f"✗ Connection failed: {e}")
                raise

        @task
        def test_endpoint(self):
            try:
                response = self.client.get("/api/test")
            except ConnectionError as e:
                print(f"Connection error: {e}")
            except requests.exceptions.Timeout:
                print("Request timeout")

**Debugging Steps:**

1. Verify the target is running:

   .. code-block:: bash

       curl -v http://target-url:port/

2. Check DNS resolution:

   .. code-block:: bash

       nslookup target-url

3. Verify network connectivity:

   .. code-block:: bash

       ping target-url

4. Check firewall rules:

   .. code-block:: bash

       # On target machine
       sudo netstat -tlnp | grep LISTEN

.. _error-timeout:

Timeout Errors
--------------

**Symptoms:**
- Error: `Connection timeout`
- Error: `Read timed out`
- Requests never complete

**Possible Causes:**
1. Target is responding slowly
2. Timeout is set too low
3. Network latency is high
4. Target is overloaded

**Solutions:**

.. code-block:: python

    from locust import HttpUser, task, between

    class TimeoutHandlingUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def request_with_timeout(self):
            """Use appropriate timeout"""
            try:
                response = self.client.get(
                    "/api/endpoint",
                    timeout=10  # Increase from default 30s if needed
                )
            except requests.exceptions.Timeout:
                print("Request exceeded timeout")

**Increase Timeout:**

.. code-block:: bash

    # In locustfile.py
    timeout = 30  # seconds

    # Or per request
    self.client.get("/api/endpoint", timeout=30)

**Monitor Response Times:**

.. code-block:: python

    from locust import HttpUser, task, between, events
    import time

    class ResponseTimeMonitor(HttpUser):
        wait_time = between(1, 3)

        @task
        def slow_request(self):
            start = time.time()
            response = self.client.get("/api/slow-endpoint")
            elapsed = time.time() - start
            
            if elapsed > 5:
                print(f"Slow response: {elapsed:.2f}s")

.. _error-auth-failures:

Authentication Failures
-----------------------

**Symptoms:**
- Error: `401 Unauthorized`
- Error: `403 Forbidden`
- Requests fail after first few

**Possible Causes:**
1. Invalid credentials
2. Token expired
3. Auth header not set correctly
4. Session not maintained

**Solutions:**

**Bearer Token Issues:**

.. code-block:: python

    from locust import HttpUser, task, between

    class TokenAuthUser(HttpUser):
        wait_time = between(1, 3)
        token = None

        def on_start(self):
            """Get fresh token"""
            response = self.client.post(
                "/api/auth/token",
                json={"username": "user", "password": "pass"}
            )
            
            if response.status_code == 200:
                self.token = response.json().get("token")
                print(f"✓ Token obtained: {self.token[:20]}...")
                self.client.headers.update({
                    "Authorization": f"Bearer {self.token}"
                })
            else:
                print(f"✗ Auth failed: {response.status_code}")
                print(f"  Response: {response.text}")

**Session Auth Issues:**

.. code-block:: python

    from locust import HttpUser, task, between

    class SessionAuthUser(HttpUser):
        wait_time = between(1, 3)

        def on_start(self):
            """Establish session"""
            response = self.client.post(
                "/login",
                data={"username": "user", "password": "pass"}
            )
            
            if response.status_code == 200:
                print("✓ Session established")
                # Cookies are automatically maintained
            else:
                print(f"✗ Login failed: {response.status_code}")

**Test Auth Locally:**

.. code-block:: bash

    # Test authentication manually
    curl -X POST http://target/api/auth/token \
         -H "Content-Type: application/json" \
         -d '{"username":"user","password":"pass"}'

.. _error-server-errors:

Server Errors (5xx)
-------------------

**Symptoms:**
- Error: `500 Internal Server Error`
- Error: `502 Bad Gateway`
- Error: `503 Service Unavailable`

**Possible Causes:**
1. Application crash or exception
2. Database connection issues
3. Resource exhaustion on server
4. Unhandled edge case triggered by load

**Solutions:**

**Monitor Error Rate:**

.. code-block:: python

    from locust import HttpUser, task, between, events

    class ErrorMonitoringUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def check_response(self):
            response = self.client.get("/api/endpoint", catch_response=True)
            
            if response.status_code >= 500:
                response.failure(f"Server error: {response.status_code}")
                print(f"Response body: {response.text}")
            else:
                response.success()

    @events.quitting.add_listener
    def on_quitting(environment, **kwargs):
        """Show error summary"""
        print("\n=== Error Summary ===")
        for name, stats in environment.stats.entries.items():
            if stats.num_failures > 0:
                print(f"{name}: {stats.num_failures} failures")

**Check Server Logs:**

.. code-block:: bash

    # If you have access to server
    tail -f /var/log/application.log
    journalctl -f  # systemd logs

.. _error-memory-exhaustion:

Memory Exhaustion
-----------------

**Symptoms:**
- Error: `MemoryError`
- Process killed (OOM killer)
- Locust crashes or freezes

**Possible Causes:**
1. Memory leak in locustfile
2. Storing too much data per user
3. Response caching unbounded
4. Connection pool too large

**Solutions:**

**Monitor Memory:**

.. code-block:: python

    from locust import HttpUser, task, between, events
    import psutil
    import os

    @events.request.add_listener
    def log_memory_usage(request_type, name, response_time, response_length, 
                         exception, context, **kwargs):
        """Log memory on each request"""
        process = psutil.Process(os.getpid())
        mem = process.memory_info().rss / 1024 / 1024
        
        if mem > 500:  # Alert if over 500 MB
            print(f"⚠ High memory: {mem:.0f} MB")

**Fix Common Leaks:**

.. code-block:: python

    from locust import HttpUser, task, between
    from collections import deque

    # ❌ WRONG - Unbounded list
    class LeakyUser(HttpUser):
        responses = []
        
        @task
        def leak_memory(self):
            response = self.client.get("/api/items")
            self.responses.append(response)  # Grows forever!

    # ✅ CORRECT - Bounded deque
    class FixedUser(HttpUser):
        responses = deque(maxlen=100)  # Max 100 items
        
        @task
        def fixed_memory(self):
            response = self.client.get("/api/items")
            self.responses.append(response)  # Stays bounded

See Also: :ref:`memory-optimization`

.. _error-cpu-bottleneck:

CPU Bottleneck
--------------

**Symptoms:**
- Test output: `CPU is likely the bottleneck`
- Cannot reach target load
- Response times degrade quickly

**Possible Causes:**
1. Test tasks are CPU-intensive
2. Using HttpUser instead of FastHttpUser
3. Processing large responses
4. Single-threaded bottleneck

**Solutions:**

**Use FastHttpUser:**

.. code-block:: python

    # ❌ WRONG - HttpUser is CPU-heavy
    from locust import HttpUser
    class SlowUser(HttpUser):
        pass

    # ✅ CORRECT - FastHttpUser is efficient
    from locust.contrib.fasthttp import FastHttpUser
    class FastUser(FastHttpUser):
        pass

**Reduce CPU Work Per Request:**

.. code-block:: python

    from locust import HttpUser, task, between

    # ❌ WRONG - Heavy processing
    class CPUIntensiveUser(HttpUser):
        @task
        def heavy_processing(self):
            response = self.client.get("/api/data")
            data = response.json()
            # Process ALL data
            results = [expensive_computation(item) for item in data]

    # ✅ CORRECT - Minimal processing
    class EfficientUser(HttpUser):
        @task
        def minimal_processing(self):
            response = self.client.get("/api/data")
            # Just check status code, don't process

**Run Distributed:**

.. code-block:: bash

    # Run master and workers on separate machines
    # Master
    locust -f locustfile.py --master

    # Workers (on different machines)
    locust -f locustfile.py --worker --master-host=master-ip

Performance Issues
==================

Slow Response Times
-------------------

**Investigate:**

.. code-block:: python

    from locust import HttpUser, task, between, events
    import statistics

    response_times = []

    @events.request.add_listener
    def track_response_time(request_type, name, response_time, **kwargs):
        response_times.append(response_time)

    @events.quitting.add_listener
    def show_stats(environment, **kwargs):
        if response_times:
            print(f"Average: {statistics.mean(response_times):.0f}ms")
            print(f"Median: {statistics.median(response_times):.0f}ms")
            print(f"95th percentile: {statistics.quantiles(response_times, n=20)[18]:.0f}ms")
            print(f"Max: {max(response_times):.0f}ms")

Uneven Load Distribution
------------------------

**Symptoms:**
- Some workers have much higher load than others
- Load distribution not balanced in distributed mode

**Solutions:**

.. code-block:: bash

    # Ensure equal user distribution
    locust -f locustfile.py --master \
           --worker-bind-cpu  # Bind each worker to a CPU core

Distributed Mode Issues
=======================

Master and Workers Don't Connect
---------------------------------

**Symptoms:**
- Workers show "Waiting for orders"
- Stats never update

**Solutions:**

1. **Check Network Connectivity:**

   .. code-block:: bash

       # From worker machine
       telnet master-ip 5557

2. **Check Firewall:**

   .. code-block:: bash

       # Master listens on port 5557 (events) and 5558 (comms)
       sudo netstat -tlnp | grep 5557

3. **Use Correct Master IP:**

   .. code-block:: bash

       # Worker
       locust -f locustfile.py --worker --master-host=correct-master-ip

Uneven User Distribution
------------------------

**Symptoms:**
- One worker has 1000 users, another has 10

**Solutions:**

.. code-block:: bash

    # Explicitly set user count per worker
    locust -f locustfile.py --master -u 1000 -c 10

Test Not Starting
==================

Users Don't Spawn
-----------------

**Symptoms:**
- No users start spawning
- "Waiting for command" in UI

**Solutions:**

1. Check locustfile syntax:

   .. code-block:: bash

       python -m py_compile locustfile.py

2. Check user class definition:

   .. code-block:: python

       from locust import HttpUser, task, between

       # ✅ CORRECT
       class MyUser(HttpUser):
           @task
           def my_task(self):
               pass

       # ❌ WRONG - Missing @task or methods
       class BadUser(HttpUser):
           pass

3. Try starting with command line:

   .. code-block:: bash

       locust -f locustfile.py --host=http://localhost:8000 -u 10 -c 1

Data Issues
===========

Requests Using Same Data
-------------------------

**Symptoms:**
- All requests look identical
- Testing same endpoint repeatedly

**Solutions:**

.. code-block:: python

    from locust import HttpUser, task, between
    import random

    class VariedDataUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def varied_requests(self):
            # ✅ Use random IDs
            item_id = random.randint(1, 10000)
            self.client.get(f"/api/items/{item_id}")

        @task
        def varied_search(self):
            # ✅ Use different search terms
            search_terms = ["order", "invoice", "payment", "customer"]
            term = random.choice(search_terms)
            self.client.get(f"/api/search?q={term}")

Getting Help
============

When to Check Logs
-------------------

**Always include:**
- Locust output (console)
- Target application logs
- System logs (if permission)

**Common log locations:**

.. code-block:: bash

    # Application logs
    tail -f /var/log/app/error.log
    tail -f /var/log/app/access.log

    # System logs
    journalctl -f
    tail -f /var/log/syslog

Reporting Issues
----------------

When asking for help, include:

1. Locustfile (relevant code)
2. Error message (full stacktrace)
3. Locust version: `locust --version`
4. System info: `uname -a`
5. Python version: `python --version`
6. Steps to reproduce

Example Debug Locustfile
========================

Here's a comprehensive debugging setup:

.. code-block:: python

    from locust import HttpUser, task, between, events
    import logging
    import sys

    # Configure logging
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s [%(levelname)s] %(message)s'
    )
    logger = logging.getLogger(__name__)

    class DebugUser(HttpUser):
        wait_time = between(1, 3)

        def on_start(self):
            logger.info("User starting")
            try:
                response = self.client.get("/")
                logger.info(f"Connectivity check: {response.status_code}")
            except Exception as e:
                logger.error(f"Connectivity failed: {e}")

        @task
        def debug_request(self):
            logger.info("Making request")
            response = self.client.get("/api/items", catch_response=True)
            
            if response.status_code == 200:
                response.success()
                logger.debug(f"Success: {len(response.content)} bytes")
            else:
                response.failure(f"Status {response.status_code}")
                logger.error(f"Failed response: {response.text}")

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        logger.info("Test starting")

    @events.test_stop.add_listener
    def on_test_stop(environment, **kwargs):
        logger.info("Test stopping")

    @events.request.add_listener
    def on_request(request_type, name, response_time, response_length, 
                   exception, context, **kwargs):
        if exception:
            logger.error(f"Request failed: {name} - {exception}")

See Also
========

* :ref:`writing-a-locustfile` - Writing locustfiles
* :ref:`common-patterns` - Common patterns and examples
* :ref:`memory-optimization` - Memory optimization
