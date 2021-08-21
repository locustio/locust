.. _testing-request-sdks:

=============================
testing-requests-based SDK's
=============================


Example: Patching over SDK's that wrap around Session objects
=============================================================

If you have a prebuilt SDK for a target system that is a essentially a wrapper for Session object.
You can use the a pattern of patching over the internal session object with the locust provided one:

.. literalinclude:: ../examples/sdk_session_patching/session_patch_locustfile.py


