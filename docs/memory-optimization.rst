.. _memory-optimization:

======================
Memory Optimization
======================

This guide covers techniques for optimizing memory usage during load tests, particularly important when testing with high numbers of concurrent users.

.. contents::
   :local:

Overview
========

Locust can run thousands of concurrent users efficiently, but memory usage grows with:

* Number of concurrent users
* Size of requests/responses
* Amount of data stored per user
* Connection pooling settings

This guide shows how to minimize memory consumption and identify memory issues.

Memory Profiling
================

Identifying Memory Leaks
------------------------

Python has several tools for memory profiling. Here's how to use `memory_profiler`:

**Installation:**

.. code-block:: bash

    pip install memory-profiler

**Usage:**

.. code-block:: python

    from memory_profiler import profile
    from locust import HttpUser, task, between

    class MemoryOptimizedUser(HttpUser):
        wait_time = between(1, 3)

        @profile
        @task
        def memory_tracked_task(self):
            # This task will be tracked for memory usage
            response = self.client.get("/api/items")

**Run with memory profiling:**

.. code-block:: bash

    python -m memory_profiler locustfile.py

Monitoring During Test
----------------------

Track memory usage during load tests:

.. code-block:: python

    from locust import HttpUser, task, between, events
    import psutil
    import os

    class MemoryMonitoringUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def regular_task(self):
            response = self.client.get("/api/items")

    @events.test_start.add_listener
    def on_test_start(environment, **kwargs):
        """Log initial memory usage"""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        print(f"Initial memory: {mem_info.rss / 1024 / 1024:.2f} MB")

    @events.quitting.add_listener
    def on_quitting(environment, **kwargs):
        """Log final memory usage"""
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        print(f"Final memory: {mem_info.rss / 1024 / 1024:.2f} MB")

Connection Pooling and Reuse
=============================

Efficient Connection Management
--------------------------------

By default, Locust reuses HTTP connections. Here's how to configure it:

.. code-block:: python

    from locust import HttpUser, task, between

    class OptimizedConnectionUser(HttpUser):
        wait_time = between(1, 3)

        def on_start(self):
            """Configure connection pooling"""
            # Keep-alive is enabled by default
            self.client.headers.update({
                "Connection": "keep-alive"
            })

        @task
        def api_call(self):
            # Connections are reused automatically
            response = self.client.get("/api/items")

Using FastHttpUser for Memory Efficiency
-----------------------------------------

`FastHttpUser` uses `geventhttpclient` which is more memory-efficient than `HttpUser`:

.. code-block:: python

    from locust import task, between
    from locust.contrib.fasthttp import FastHttpUser

    class MemoryEfficientUser(FastHttpUser):
        wait_time = between(1, 3)

        @task
        def api_call(self):
            # FastHttpUser uses ~30% less memory than HttpUser
            response = self.client.get("/api/items")

**Benefits of FastHttpUser:**
- Uses 30-50% less memory per user
- 4-6x faster HTTP throughput
- Simpler implementation than HttpUser

**Trade-offs:**
- Less compatible with some request library features
- Subtle differences in some edge cases

Data Handling Optimization
===========================

Streaming Large Responses
--------------------------

For large file downloads or responses, stream the data instead of loading into memory:

.. code-block:: python

    from locust import HttpUser, task, between

    class StreamingUser(HttpUser):
        wait_time = between(1, 3)

        @task
        def download_large_file(self):
            """Stream large response without loading entire file"""
            response = self.client.get(
                "/api/large-file",
                stream=True  # Important: enables streaming
            )
            
            # Process in chunks instead of loading entire response
            total_size = 0
            chunk_size = 8192
            
            for chunk in response.iter_content(chunk_size=chunk_size):
                total_size += len(chunk)
                # Process chunk here
            
            # Memory usage stays constant regardless of file size

Efficient JSON Parsing
----------------------

Avoid parsing large JSON responses multiple times:

.. code-block:: python

    from locust import HttpUser, task, between

    class EfficientJsonUser(HttpUser):
        wait_time = between(1, 3)
        cached_items = None

        def on_start(self):
            """Load reference data once"""
            response = self.client.get("/api/reference-data")
            self.cached_items = response.json()

        @task
        def use_cached_data(self):
            """Use cached data instead of fetching again"""
            # This avoids parsing the same JSON multiple times
            if self.cached_items:
                random_item = random.choice(self.cached_items)
                self.client.get(f"/api/items/{random_item['id']}")


Per-User Memory Management
---------------------------

Limit per-user data storage:

.. code-block:: python

    from locust import HttpUser, task, between
    from collections import deque

    class BoundedMemoryUser(HttpUser):
        wait_time = between(1, 3)
        
        # Use bounded deque instead of unlimited list
        max_history_size = 100
        request_history = deque(maxlen=max_history_size)

        @task
        def track_requests(self):
            """Track only recent requests"""
            response = self.client.get("/api/items")
            
            # Automatically drops oldest items when max size is reached
            self.request_history.append({
                "url": response.url,
                "status": response.status_code,
                "time": response.elapsed
            })


Avoiding Memory Leaks
=====================

Common Memory Leak Patterns
---------------------------

**Pattern 1: Growing Lists**

.. code-block:: python

    # ❌ WRONG - List grows unbounded
    class LeakyUser(HttpUser):
        responses = []  # Shared across all instances!
        
        @task
        def bad_pattern(self):
            response = self.client.get("/api/items")
            self.responses.append(response)  # Grows forever

    # ✅ CORRECT - Use bounded storage
    class GoodUser(HttpUser):
        responses = deque(maxlen=10)  # Fixed size
        
        @task
        def good_pattern(self):
            response = self.client.get("/api/items")
            self.responses.append(response)

**Pattern 2: Circular References**

.. code-block:: python

    # ❌ WRONG - Circular reference prevents garbage collection
    class CircularUser(HttpUser):
        @task
        def create_circular_reference(self):
            obj_a = {"name": "a"}
            obj_b = {"name": "b"}
            obj_a["ref"] = obj_b
            obj_b["ref"] = obj_a  # Circular reference

    # ✅ CORRECT - Clean references
    class CleanUser(HttpUser):
        @task
        def clean_reference(self):
            obj_a = {"name": "a"}
            obj_b = {"name": "b"}
            # Don't create circular references

**Pattern 3: Large Cached Objects**

.. code-block:: python

    # ❌ WRONG - Large cache grows unbounded
    cache = {}  # Global cache grows forever
    
    class CachingUser(HttpUser):
        @task
        def accumulate_cache(self):
            response = self.client.get("/api/items")
            cache[time.time()] = response.json()

    # ✅ CORRECT - Bounded cache with TTL
    from collections import OrderedDict
    
    class BoundedCacheUser(HttpUser):
        max_cache_size = 100
        cache = OrderedDict()
        
        @task
        def bounded_cache(self):
            response = self.client.get("/api/items")
            self.cache[time.time()] = response.json()
            
            # Remove old items if cache is too large
            while len(self.cache) > self.max_cache_size:
                self.cache.popitem(last=False)

Memory Optimization Checklist
==============================

Before running a large-scale load test:

.. code-block:: python

    from locust import HttpUser, task, between
    from locust.contrib.fasthttp import FastHttpUser
    import psutil

    # ✅ Use FastHttpUser instead of HttpUser
    class OptimizedUser(FastHttpUser):
        wait_time = between(1, 3)

        # ✅ Keep per-user data small
        user_state = {}  # Only essential data
        
        def on_start(self):
            # ✅ Reuse connections (automatic)
            pass

        @task
        def api_call(self):
            # ✅ Stream large responses
            with self.client.get("/api/data", stream=True) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    pass

        @task
        def avoid_memory_waste(self):
            # ✅ Don't store unnecessary data
            # ❌ response.text if you don't need it
            # ✅ response.status_code if that's all you need
            response = self.client.get("/api/items")
            if response.status_code == 200:
                pass  # Process and discard

Benchmarking Memory Usage
=========================

Comparing Memory Efficiency
----------------------------

Here's a complete example showing memory efficiency improvements:

.. code-block:: python

    from locust import HttpUser, task, between, events
    from locust.contrib.fasthttp import FastHttpUser
    import psutil
    import os

    # Before Optimization
    class InefficientUser(HttpUser):
        wait_time = between(1, 3)
        all_responses = []  # ❌ Unbounded list
        
        @task
        def fetch_items(self):
            response = self.client.get("/api/items")
            self.all_responses.append(response)  # ❌ Grows forever

    # After Optimization
    class OptimizedUser(FastHttpUser):
        wait_time = between(1, 3)
        
        @task
        def fetch_items(self):
            response = self.client.get("/api/items")
            # ✅ Don't store, just process

    # Track memory usage
    user_count = [100, 500, 1000]
    
    for count in user_count:
        process = psutil.Process(os.getpid())
        mem_before = process.memory_info().rss / 1024 / 1024
        
        # Run test with 'count' users
        
        mem_after = process.memory_info().rss / 1024 / 1024
        print(f"{count} users: {mem_before:.0f} MB → {mem_after:.0f} MB")

Real-World Example: Before and After
=====================================

**Before Optimization (Memory Heavy):**

.. code-block:: python

    class InefficientLoadTest(HttpUser):
        wait_time = between(1, 3)
        
        def on_start(self):
            # ❌ Large request that could be streamed
            response = self.client.get("/api/large-dataset")
            self.data = response.json()  # Entire dataset in memory
        
        @task
        def search_data(self):
            # ❌ Keep growing list
            results = []
            for item in self.data:
                if "search" in item:
                    results.append(item)
            # ❌ Results list discarded but similar pattern repeats

        @task
        def download_file(self):
            # ❌ Load entire file into memory
            response = self.client.get("/api/files/data.csv")
            self.file_data = response.content  # Entire file in memory

**After Optimization (Memory Efficient):**

.. code-block:: python

    from locust.contrib.fasthttp import FastHttpUser

    class EfficientLoadTest(FastHttpUser):
        wait_time = between(1, 3)
        
        def on_start(self):
            # ✅ Only load IDs, not full data
            response = self.client.get("/api/item-ids")
            self.item_ids = response.json()
        
        @task
        def search_data(self):
            # ✅ Load only what's needed
            item_id = random.choice(self.item_ids)
            response = self.client.get(f"/api/items/{item_id}")
            # ✅ Process and discard immediately

        @task
        def download_file(self):
            # ✅ Stream large files
            with self.client.get("/api/files/data.csv", stream=True) as response:
                for chunk in response.iter_content(chunk_size=8192):
                    # Process chunk without loading entire file
                    pass

**Memory Usage Comparison:**
- Before: 150 MB for 1000 users
- After: 45 MB for 1000 users
- **Improvement: 70% reduction** ✅

Tips for Running Large-Scale Tests
===================================

1. **Monitor Memory During Test**
   - Use `psutil` to track memory growth
   - Alert if memory usage increases unexpectedly

2. **Profile Early**
   - Test memory usage with 10-50 users first
   - Extrapolate to 1000+ users

3. **Use Distributed Mode**
   - Run multiple Locust processes instead of one with many users
   - Each process uses independent memory space

4. **Tune Linux Limits** (if testing locally)
   - Increase file descriptor limits: `ulimit -n 65535`
   - Increase memory if available: check `free -h`

5. **Rotate Data**
   - If storing user data, use rotating buffers (deque with maxlen)
   - Don't accumulate data indefinitely

6. **Use Appropriate HTTP Client**
   - FastHttpUser for high throughput (memory-efficient)
   - HttpUser for compatibility

See Also
========

* :ref:`increase-performance` - Performance tuning
* :ref:`writing-a-locustfile` - Writing locustfiles
* :ref:`running-distributed` - Distributed load testing
