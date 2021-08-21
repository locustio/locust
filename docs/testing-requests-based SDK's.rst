.. _testing-request-sdks:

=============================
Testing Requests based SDKs
=============================

If a prebuilt SDK is available for your target system. Locust has a supported pattern for integrating
it's usage into your load testing efforts.

The only perquisite to achieve this; is that the SDK needs to have an accessible ``request.Sessions``
class.

The following example shows the locust client overwriting the internal ``_session`` object of ``Archivist`` SDK
during startup.

.. literalinclude:: ../examples/sdk_session_patching/session_patch_locustfile.py


