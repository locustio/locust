import re
import time

import requests
from requests import Request, Response
from requests.auth import HTTPBasicAuth
from requests.exceptions import (InvalidSchema, InvalidURL, MissingSchema,
                                 RequestException)

from urllib.parse import urlparse, urlunparse

from .exception import CatchResponseError, ResponseError

absolute_http_url_regexp = re.compile(r"^https?://", re.I)


class LocustResponse(Response):

    def raise_for_status(self):
        if hasattr(self, 'error') and self.error:
            raise self.error
        Response.raise_for_status(self)


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
    from a User class' host property.
    
    Each of the methods for making requests also takes two additional optional arguments which 
    are Locust specific and doesn't exist in python-requests. These are:
    
    :param name: (optional) An argument that can be specified to use as label in Locust's statistics instead of the URL path. 
                 This can be used to group different URL's that are requested into a single entry in Locust's statistics.
    :param catch_response: (optional) Boolean argument that, if set, can be used to make a request return a context manager 
                           to work as argument to a with statement. This will allow the request to be marked as a fail based on the content of the 
                           response, even if the response code is ok (2xx). The opposite also works, one can use catch_response to catch a request
                           and then mark it as successful even if the response code was not (i.e 500 or 404).
    """
    def __init__(self, base_url, request_success, request_failure, *args, **kwargs):
        super(HttpSession, self).__init__(*args, **kwargs)
        
        self.base_url = base_url
        self.request_success = request_success
        self.request_failure = request_failure
        
        # Check for basic authentication
        parsed_url = urlparse(self.base_url)
        if parsed_url.username and parsed_url.password:
            netloc = parsed_url.hostname
            if parsed_url.port:
                netloc += ":%d" % parsed_url.port
            
            # remove username and password from the base_url
            self.base_url = urlunparse((parsed_url.scheme, netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))
            # configure requests to use basic auth
            self.auth = HTTPBasicAuth(parsed_url.username, parsed_url.password)
    
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
        :param files: (optional) Dictionary of ``'filename': file-like-objects`` for multipart encoding upload.
        :param auth: (optional) Auth tuple or callable to enable Basic/Digest/Custom HTTP Auth.
        :param timeout: (optional) How long in seconds to wait for the server to send data before giving up, as a float, 
            or a (`connect timeout, read timeout <user/advanced.html#timeouts>`_) tuple.
        :type timeout: float or tuple
        :param allow_redirects: (optional) Set to True by default.
        :type allow_redirects: bool
        :param proxies: (optional) Dictionary mapping protocol to the URL of the proxy.
        :param stream: (optional) whether to immediately download the response content. Defaults to ``False``.
        :param verify: (optional) if ``True``, the SSL cert will be verified. A CA_BUNDLE path can also be provided.
        :param cert: (optional) if String, path to ssl client cert file (.pem). If Tuple, ('cert', 'key') pair.
        """
        
        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(url)
        
        # store meta data that is used when reporting the request to locust's statistics
        request_meta = {}
        
        # set up pre_request hook for attaching meta data to the request object
        request_meta["method"] = method
        request_meta["start_time"] = time.monotonic()
        
        response = self._send_request_safe_mode(method, url, **kwargs)
        
        # record the consumed time
        request_meta["response_time"] = (time.monotonic() - request_meta["start_time"]) * 1000
        
    
        request_meta["name"] = name or (response.history and response.history[0] or response).request.path_url
        
        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        if kwargs.get("stream", False):
            request_meta["content_size"] = int(response.headers.get("content-length") or 0)
        else:
            request_meta["content_size"] = len(response.content or b"")
        
        if catch_response:
            response.locust_request_meta = request_meta
            return ResponseContextManager(response, request_success=self.request_success, request_failure=self.request_failure)
        else:
            if name:
                # Since we use the Exception message when grouping failures, in order to not get 
                # multiple failure entries for different URLs for the same name argument, we need 
                # to temporarily override the response.url attribute
                orig_url = response.url
                response.url = name
            try:
                response.raise_for_status()
            except RequestException as e:
                self.request_failure.fire(
                    request_type=request_meta["method"], 
                    name=request_meta["name"], 
                    response_time=request_meta["response_time"], 
                    response_length=request_meta["content_size"],
                    exception=e, 
                )
            else:
                self.request_success.fire(
                    request_type=request_meta["method"],
                    name=request_meta["name"],
                    response_time=request_meta["response_time"],
                    response_length=request_meta["content_size"],
                )
            if name:
                response.url = orig_url
            return response
    
    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send an HTTP request, and catch any exception that might occur due to connection problems.
        
        Safe mode has been removed from requests 1.x.
        """
        try:
            return super().request(method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL):
            raise
        except RequestException as e:
            r = LocustResponse()
            r.error = e
            r.status_code = 0  # with this status_code, content returns None
            r.request = Request(method, url).prepare() 
            return r


class ResponseContextManager(LocustResponse):
    """
    A Response class that also acts as a context manager that provides the ability to manually 
    control if an HTTP request should be marked as successful or a failure in Locust's statistics
    
    This class is a subclass of :py:class:`Response <requests.Response>` with two additional 
    methods: :py:meth:`success <locust.clients.ResponseContextManager.success>` and 
    :py:meth:`failure <locust.clients.ResponseContextManager.failure>`.
    """
    
    _manual_result = None
    
    def __init__(self, response, request_success, request_failure):
        # copy data from response to this object
        self.__dict__ = response.__dict__
        self._request_success = request_success
        self._request_failure = request_failure
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc, value, traceback):
        if self._manual_result is not None:
            if self._manual_result == True:
                self._report_success()
            elif isinstance(self._manual_result, Exception):
                self._report_failure(self._manual_result)
            
            # if the user has already manually marked this response as failure or success
            # we can ignore the default behaviour of letting the response code determine the outcome
            return exc is None
        
        if exc:
            if isinstance(value, ResponseError):
                self._report_failure(value)
            else:
                # we want other unknown exceptions to be raised
                return False
        else:
            try:
                self.raise_for_status()
            except requests.exceptions.RequestException as e:
                self._report_failure(e)
            else:
                self._report_success()
        
        return True
    
    def _report_success(self):
        self._request_success.fire(
            request_type=self.locust_request_meta["method"],
            name=self.locust_request_meta["name"],
            response_time=self.locust_request_meta["response_time"],
            response_length=self.locust_request_meta["content_size"],
        )
    
    def _report_failure(self, exc):
        self._request_failure.fire(
            request_type=self.locust_request_meta["method"],
            name=self.locust_request_meta["name"],
            response_time=self.locust_request_meta["response_time"],
            response_length=self.locust_request_meta["content_size"],
            exception=exc,
        )
    
    def success(self):
        """
        Report the response as successful
        
        Example::
        
            with self.client.get("/does/not/exist", catch_response=True) as response:
                if response.status_code == 404:
                    response.success()
        """
        self._manual_result = True
    
    def failure(self, exc):
        """
        Report the response as a failure.
        
        if exc is anything other than a python exception (like a string) it will
        be wrapped inside a CatchResponseError. 
        
        Example::
        
            with self.client.get("/", catch_response=True) as response:
                if response.content == b"":
                    response.failure("No data")
        """
        if not isinstance(exc, Exception):
            exc = CatchResponseError(exc)
        self._manual_result = exc
