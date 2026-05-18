===================
aiolocust / asyncio
===================


`aiolocust <https://github.com/cyberw/aiolocust>`_ is a 2026 reimagining of Locust.

It uses `asyncio <https://docs.python.org/3/library/asyncio.html>`_/`aiohttp <https://docs.aiohttp.org/en/stable/>`_ instead of gevent/requests and leverages modern Python.

.. code-block:: python

    import asyncio
    from aiolocust import HttpUser

    async def run(user: HttpUser):
        async with user.client.get("http://example.com/") as resp:
            pass
        async with user.client.get("http://example.com/") as resp:
            # extra validation, not just HTTP response code:
            assert "expected text" in await resp.text()
        await asyncio.sleep(0.1)

It has less features than Locust and aims to be more minimalistic, relying on OTEL for more complex visualization and analysis.

It is currently maintained as `a separate project <https://github.com/cyberw/aiolocust>`_, but may be merged and/or shipped with Locust in the future.

