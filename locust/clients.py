import re
import time
from collections import namedtuple
from urlparse import urlparse, urlunparse

import requests
from requests.auth import HTTPBasicAuth
from requests.exceptions import RequestException

import events
from exception import CatchResponseError, ResponseError

absolute_http_url_regexp = re.compile(r"^https?://", re.I)


class HttpSession(requests.Session):
    """
    Class for performing web requests and holding (session-) cookies between requests (in order
    to be able to log in and out of websites). Each request is logged so that locust can display 
    statistics.
    
    This is a slightly extended version of `python-request <http://python-requests.org>`_'s
    :py:class:`requests.Session` class and mostly this class works exactly the same. However 
    the methods for making requests (get, post, delete, put, head, options, patch, request) 
    can now take a *url* argument that's only the path part of the URL, in which case the host 
    part of the URL will be prepended with the HttpSession.base_url which is normally inherited
    from a Locust class' host property.
    
    Each of the methods for making requests also takes two additional optional arguments which 
    are Locust specific and doesn't exist in python-requests. These are:
    
    :param name: (optional) An argument that can be specified to use as label in Locust's statistics instead of the URL path. 
                 This can be used to group different URL's that are requested into a single entry in Locust's statistics.
    :param catch_response: (optional) Boolean argument that, if set, can be used to make a request return a context manager 
                           to work as argument to a with statement. This will allow the request to be marked as a fail based on the content of the 
                           response, even if the response code is ok (2xx). The opposite also works, one can use catch_response to catch a request
                           and then mark it as successful even if the response code was not (i.e 500 or 404).
    """
    def __init__(self, base_url, *args, **kwargs):
        self.base_url = base_url
        
        # Check for basic authentication
        parsed_url = urlparse(self.base_url)
        if parsed_url.username and parsed_url.password:
            netloc = parsed_url.hostname
            if parsed_url.port:
                netloc += ":%d" % parsed_url.port
            
            # remove username and password from the base_url
            self.base_url = urlunparse((parsed_url.scheme, netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))
            # configure requests to use basic auth
            kwargs["auth"] = HTTPBasicAuth(parsed_url.username, parsed_url.password)
        
        # requests config
        config = {
            "max_retries": 0,
            "keep_alive": False,
        }.update(kwargs.get("config", {}))
        kwargs["config"] = config
        
        super(HttpSession, self).__init__(*args, **kwargs)
    
    def _build_url(self, path):
        """ prepend url with hostname unless it's already an absolute URL """
        if absolute_http_url_regexp.match(path):
            return path
        else:
            return "%s%s" % (self.base_url, path)
    
    def request(self, method, url, name=None, catch_response=False, **kwargs):
        """
        Constructs and sends a :py:class:`requests.Request`.
        Returns :py:class:`requests.Response` object.

        :param method: method for the new :class:`Request` object.
        :param url: URL for the new :class:`Request` object.
        :param name: (optional) An argument that can be specified to use as label in Locust's statistics instead of the URL path. 
          This can be used to group different URL's that are requested into a single entry in Locust's statistics.
        :param catch_response: (optional) Boolean argument that, if set, can be used to make a request return a context manager 
          to work as argument to a with statement. This will allow the request to be marked as a fail based on the content of the 
          response, even if the response code is ok (2xx). The opposite also works, one can use catch_response to catch a request
          and then mark it as successful even if the response code was not (i.e 500 or 404).
        :param params: (optional) Dictionary or bytes to be sent in the query string for the :class:`Request`.
        :param data: (optional) Dictionary or bytes to send in the body of the :class:`Request`.
        :param headers: (optional) Dictionary of HTTP Headers to send with the :class:`Request`.
        :param cookies: (optional) Dict or CookieJar object to send with the :class:`Request`.
        :param files: (optional) Dictionary of 'filename': file-like-objects for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) Float describing the timeout of the request.
        :param allow_redirects: (optional) Boolean. Set to True by default.
        :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
        :param return_response: (optional) If False, an un-sent Request object will returned.
        :param config: (optional) A configuration dictionary. See ``request.defaults`` for allowed keys and their default values.
        :param prefetch: (optional) whether to immediately download the response content. Defaults to ``True``.
        :param verify: (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
        :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        """
        
        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(url)
        
        request_meta = {}
        
        # set up pre and post request hooks for recording the requests in the statistics
        def on_pre_request(request):
            request.locust_request_meta = request_meta
            request_meta["method"] = request.method
            request_meta["name"] = name or request.path_url
            request_meta["start_time"] = time.time()
        
        def on_response(response):
            request = response.request
            request_meta["response_time"] = int((time.time() - request_meta["start_time"]) * 1000)
            
            if not catch_response:
                # if catch_response is set, the reporting of the request as fail or success, is to
                # be done in ResponseContextManager
                try:
                    response.raise_for_status()
                except requests.exceptions.RequestException, e:
                    events.request_failure.fire(request_meta["method"], request_meta["name"], request_meta["response_time"], e, response)
                else:
                    events.request_success.fire(request_meta["method"], request_meta["name"], request_meta["response_time"], int(response.headers.get("content-length") or 0))
        
        kwargs["hooks"] = {"pre_request":on_pre_request, "response":on_response}
        try:
            response = super(HttpSession, self).request(method, url, **kwargs)
        except RequestException, e:
            # If a RequestException (DNS error, could not connect, timeouts etc.) is raised, 
            # we want to report the request as a failure, but we still want the exception to 
            # be raised, so that we keep the behaviour of the python-requests lib
            request_meta["response_time"] = int((time.time() - request_meta["start_time"]) * 1000)
            events.request_failure.fire(request_meta["method"], request_meta["name"], request_meta["response_time"], e, None)
            raise
        
        if catch_response:
            return ResponseContextManager(response)
        else:
            return response

class ResponseContextManager(requests.Response):
    """
    A Response class that also acts as a context manager that provides the ability to manually 
    control if an HTTP request should be marked as successful or a failure in Locust's statistics
    
    This class is a subclass of :py:class:`Response <requests.Response>` with two additional 
    methods: :py:meth:`success <locust.clients.ResponseContextManager.success>` and 
    :py:meth:`failure <locust.clients.ResponseContextManager.failure>`.
    """
    
    _is_reported = False
    
    def __init__(self, response):
        # copy data from response to this object
        self.__dict__ = response.__dict__
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc, value, traceback):
        if self._is_reported:
            # if the user has already manually marked this response as failure or success
            # we can ignore the default haviour of letting the response code determine the outcome
            return exc is None
        
        if exc:
            if isinstance(value, ResponseError):
                self.failure(value)
            else:
                return False
        else:
            try:
                self.raise_for_status()
            except requests.exceptions.RequestException, e:
                self.failure(e)
            else:
                self.success()
        return True
    
    def success(self):
        """
        Report the response as successful
        
        Example::
        
            with self.client.get("/does/not/exist", catch_response=True) as response:
                if response.status_code == 404:
                    response.success()
        """
        events.request_success.fire(
            self.request.locust_request_meta["method"],
            self.request.locust_request_meta["name"],
            self.request.locust_request_meta["response_time"],
            int(self.headers.get("content-length") or 0),
        )
        self._is_reported = True
    
    def failure(self, exc):
        """
        Report the response as a failure.
        
        exc can be either a python exception, or a string in which case it will
        be wrapped inside a CatchResponseError. 
        
        Example::
        
            with self.client.get("/", catch_response=True) as response:
                if response.content == "":
                    response.failure("No data")
        """
        if isinstance(exc, basestring):
            exc = CatchResponseError(exc)
        
        events.request_failure.fire(
            self.request.locust_request_meta["method"],
            self.request.locust_request_meta["name"],
            self.request.locust_request_meta["response_time"],
            exc,
            self,
        )
        self._is_reported = True
