.. _distributed-limitations:

===============================
Distributed Mode Limitations
===============================

When using distributed mode with ``-f -`` (getting locustfile from master), there are important limitations to be aware of:

Single File Only
================

The ``-f -`` feature only works with single locustfiles. If your test setup uses multiple files or modules, this approach will not work.

**This will NOT work:**

.. code-block:: bash

    # Multiple files - will fail
    locust -f locustfile.py -f common.py --worker --master-host <host>
    
    # Imports from other modules - will fail  
    locust -f - --worker --master-host <host>
    # When locustfile.py contains: from common import helper_functions

**Error you'll see:**
::

    ModuleNotFoundError: No module named 'common'

Workarounds
===========

If you need to use multiple files in distributed mode, consider these alternatives:

1. **Combine into single file**: Merge all your code into one locustfile
2. **Use traditional approach**: Copy all files to each worker machine and use ``-f locustfile.py``
3. **Use locust-swarm**: Though deprecated, it handles multi-file distribution
4. **Container approach**: Package your test files in a Docker image

Example Single File Structure
=============================

Instead of splitting across files, structure everything in one file:

.. code-block:: python

    # locustfile.py - everything in one file
    from locust import HttpUser, task, between
    
    # Helper functions (previously in common.py)
    def helper_function():
        return "helper data"
    
    # User classes
    class WebsiteUser(HttpUser):
        wait_time = between(1, 3)
        
        @task
        def index_page(self):
            data = helper_function()  # Use helper directly
            self.client.get("/")

This limitation exists because the ``-f -`` feature was designed for simple, single-file test scenarios to reduce complexity in distributed setups.