import re
import time
from collections import namedtuple
from urlparse import urlparse, urlunparse

import requests
from requests.auth import HTTPBasicAuth

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
    def __init__(self, *args, **kwargs):
        self.base_url = kwargs.pop("base_url")
        
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
        
        super(HttpSession, self).__init__(self, *args, **kwargs)
    
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
        
        """
        Send the actual request using requests.Session's request() method but first
        we install event hooks that will report the request as a success or a failure, 
        to locust's statistics
        """
        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(url)
        
        # set up pre and post request hooks for recording the requests in the statistics
        def on_pre_request(request):
            request.locust_start_time = time.time()
        
        def on_response(response):
            request = response.request
            request.locust_response_time = int((time.time() - request.locust_start_time) * 1000)
            
            if not catch_response:
                try:
                    response.raise_for_status()
                except requests.exceptions.RequestException, e:
                    events.request_failure.fire(request.method, name or request.path_url, request.locust_response_time, e, response)
                else:
                    events.request_success.fire(request.method, name or request.path_url, request.locust_response_time, response)
        
        kwargs["hooks"] = {"pre_request":on_pre_request, "response":on_response}
        response = super(HttpSession, self).request(method, url, **kwargs)
        if catch_response:
            return CatchedResponse(response, name=name)
        else:
            return response


class CatchedResponse(object):
    """
    Context manager that allows for manually controlling if an HTTP request should be marked
    as successful or a failure. 
    """
    
    response = None
    """ The :py:class:`Response <requests.Response>` object that was returned"""
    
    request = None
    """ The original :py:class:`Request <requests.Request>` object that was constructed for making the HTTP request"""
    
    def __init__(self, response, name=None):
        self.response = response
        self.request = response.request
        self.name = name
        self._is_reported = False
    
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
                self.response.raise_for_status()
            except requests.exceptions.RequestException, e:
                self.failure(e)
            else:
                self.success()
        return True
    
    def success(self):
        """
        Report the current response as successful
        """
        events.request_success.fire(
            self.request.method,
            self.name or self.request.path_url,
            self.request.locust_response_time,
            self.response,
        )
        self._is_reported = True
    
    def failure(self, exc):
        """
        Report the current response as a failure.
        
        exc can be either a python exception, or a string in which case it will
        be wrapped inside a CatchResponseError. 
        
        Example::
        
            with self.client.get("/", catch_response=True) as catched:
                if catched.response.content == "":
                    catched.failure("No data")
        """
        if isinstance(exc, basestring):
            exc = CatchResponseError(exc)
        
        events.request_failure.fire(
            self.request.method,
            self.name or self.request.path_url,
            self.request.locust_response_time,
            exc,
            self.response,
        )
        self._is_reported = True
