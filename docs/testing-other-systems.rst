===========================================
Testing other systems using custom clients
===========================================

Locust was built with HTTP as its main target. However, it can easily be extended to load test 
any request/response based system, by writing a custom client that triggers 
:py:attr:`request_success <locust.events.request_success>` and 
:py:attr:`request_failure <locust.events.request_failure>` events.

Sample XML-RPC Locust client
============================

Here is an example of a Locust class, **XmlRpcLocust**, which provides an XML-RPC client, 
**XmlRpcClient**, and tracks all requests made:

.. literalinclude:: ../examples/custom_xmlrpc_client/xmlrpc_locustfile.py

If you've written Locust tests before, you'll recognize the class called *ApiUser* which is a normal 
Locust class that has a *TaskSet* class with *tasks* in its *task_set* attribute. However, the *ApiUser* 
inherits from *XmlRpcLocust* that you can see right above ApiUser. The *XmlRpcLocust* class provides an 
instance of XmlRpcClient under the *client* attribute. The *XmlRpcClient* is a wrapper around the standard 
library's :py:class:`xmlrpclib.ServerProxy`. It  basically just proxies the function calls, but with the 
important addition of firing :py:attr:`locust.events.request_success` and :py:attr:`locust.events.request_failure` 
events, which will make all calls reported in Locust's statistics.

Here's an implementation of an XML-RPC server that would work as a server for the code above:

.. literalinclude:: ../examples/custom_xmlrpc_client/server.py
