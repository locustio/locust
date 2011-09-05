import urllib2
import urllib
import time
import base64
from urlparse import urlparse, urlunparse
from exception import ResponseError
from urllib2 import HTTPError, URLError
from httplib import BadStatusLine
import socket

from StringIO import StringIO
import gzip

import events
from locust.exception import LocustError

class NoneContext(object):
    def __enter__(self):
        return None

    def __exit__(self, exc, value, traceback):
        return True

def log_request(f):
    def _wrapper(*args, **kwargs):
        name = kwargs.get('name', args[1]) or args[1]
        if "catch_response" in kwargs:
            catch_response = kwargs["catch_response"]
            del kwargs["catch_response"]
        else:
            catch_response = False
        if "allow_http_error" in kwargs:
            allow_http_error = kwargs["allow_http_error"]
            del kwargs["allow_http_error"]
        else:
            allow_http_error = False

        try:
            start = time.time()
            try:
                retval = f(*args, **kwargs)
            except HTTPError, ex:
                if allow_http_error:
                    retval = ex.locust_http_response
                    retval.exception = ex
                else:
                    raise ex
            retval.catch_response = catch_response
            retval.allow_http_error = allow_http_error
            response_time = int((time.time() - start) * 1000)
            if catch_response:
                retval._trigger_success = lambda : events.request_success.fire(name, response_time, retval)
                retval._trigger_failure = lambda e : events.request_failure.fire(name, response_time, e, None)
            else:
                events.request_success.fire(name, response_time, retval)
            return retval
        except Exception, e:
            response_time = int((time.time() - start) * 1000)
            extra = {}

            if isinstance(e, HTTPError):
                e.msg += " (" + name + ")"
                extra = {"response": e.locust_http_response}
            elif isinstance(e, URLError) or isinstance(e, BadStatusLine):
                e.args = tuple(list(e.args) + [name])
            elif isinstance(e, socket.error):
                pass
            else:
                raise

            events.request_failure.fire(name, response_time, e, **extra)

        if catch_response:
            return NoneContext()
        return None

    return _wrapper

class HttpBasicAuthHandler(urllib2.BaseHandler):
    def __init__(self, username, password):
        self.username = username
        self.password = password

    def http_request(self, request):
        base64string = base64.encodestring('%s:%s' % (self.username, self.password)).replace('\n', '')
        request.add_header("Authorization", "Basic %s" % base64string)
        return request

class HttpResponse(object):
    """
    An instance of HttpResponse is returned by HttpBrowser's get and post functions.
    It contains response data for the request that was made.
    """

    url = None
    """URL that was requested"""

    code = None
    """HTTP response code"""

    data = None
    """Response data"""

    catch_response = False
    allow_http_error = False
    _trigger_success = None
    _trigger_failure = None


    def __init__(self, url, name, code, data, info, gzip):
        self.url = url
        self._name = name
        self.code = code
        self.data = data
        self._info = info
        self._gzip = gzip
        self._decoded = False

    @property
    def info(self):
        """
        urllib2 info object containing info about the response
        """
        return self._info()

    def _get_data(self):
        if self._gzip and not self._decoded and self._info().get("Content-Encoding") == "gzip":
            self._data = gzip.GzipFile(fileobj=StringIO(self._data)).read()
            self._decoded = True
        return self._data

    def _set_data(self, data):
        self._data = data


    def __enter__(self):
        if not self.catch_response:
            raise LocustError("If using response in a with() statement you must use catch_response=True")
        return self

    def __exit__(self, exc, value, traceback):
        if exc:
            if isinstance(value, ResponseError):
                self._trigger_failure(value)
            else:
                raise value
        else:
            self._trigger_success()
        return True

    data = property(_get_data, _set_data)

class HttpBrowser(object):
    """
    Class for performing web requests and holding session cookie between requests (in order
    to be able to log in to websites). 
    
    Logs each request so that locust can display statistics.
    """

    def __init__(self, base_url, gzip=False):
        self.base_url = base_url
        self.gzip = gzip
        handlers = [urllib2.HTTPCookieProcessor()]

        # Check for basic authentication
        parsed_url = urlparse(self.base_url)
        if parsed_url.username and parsed_url.password:

            netloc = parsed_url.hostname
            if parsed_url.port:
                netloc += ":%d" % parsed_url.port

            # remove username and password from the base_url
            self.base_url = urlunparse((parsed_url.scheme, netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment))

            auth_handler = HttpBasicAuthHandler(parsed_url.username, parsed_url.password)
            handlers.append(auth_handler)

        self.opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(self.opener)

    def get(self, path, headers={}, name=None, **kwargs):
        """
        Make an HTTP GET request.
        
        Arguments:
        
        * *path* is the relative path to request.
        * *headers* is an optional dict with HTTP request headers
        * *name* is an optional argument that can be specified to use as label in the statistics instead of the path
        * *catch_response* is an optional boolean argument that, if set, can be used to make a request with a with statement.
          This will allows the request to be marked as a fail based on the content of the response, even if the
          response code is ok (2xx).
        * *allow_http_error* os an optional boolean argument, that, if set, can be used to not mark responses with
          HTTP errors as failures. If an HTTPError occurs, it will be available in the *exception* attribute of the
          response.
        
        Returns an HttpResponse instance, or None if the request failed.
        
        Example::
        
            client = HttpBrowser("http://example.com")
            response = client.get("/")
        
        Example using the with statement::
        
            from locust import ResponseError
            
            with self.client.get("/inbox", catch_response=True) as response:
                if response.data == "fail":
                    raise ResponseError("Request failed")
        """
        return self._request(path, None, headers=headers, name=name, **kwargs)

    def post(self, path, data, headers={}, name=None, **kwargs):
        """
        Make an HTTP POST request.
        
        Arguments:
        
        * *path* is the relative path to request.
        * *data* dict with the data that will be sent in the body of the POST request
        * *headers* is an optional dict with HTTP request headers
        * *name* is an optional argument that can be specified to use as label in the statistics instead of the path
        * *catch_response* is an optional boolean argument that, if set, can be used to make a request with a with statement.
          This will allows the request to be marked as a fail based on the content of the response, even if the
          response code is ok (2xx).
        * *allow_http_error* os an optional boolean argument, that, if set, can be used to not mark responses with
          HTTP errors as failures. If an HTTPError occurs, it will be available in the *exception* attribute of the
          response.
        
        Returns an HttpResponse instance, or None if the request failed.
        
        Example::
        
            client = HttpBrowser("http://example.com")
            response = client.post("/post", {"user":"joe_hill"})
        
        Example using the with statement::
        
            from locust import ResponseError
            
            with self.client.post("/inbox", {"user":"ada", content="Hello!"}, catch_response=True) as response:
                if response.data == "fail":
                    raise ResponseError("Posting of inbox message failed")
        """
        return self._request(path, data, headers=headers, name=name, **kwargs)

    @log_request
    def _request(self, path, data=None, headers={}, name=None):
        if self.gzip:
            headers["Accept-Encoding"] = "gzip"

        if data is not None:
            try:
                data = urllib.urlencode(data)
            except TypeError:
                pass # ignore if someone sends in an already prepared string

        url = self.base_url + path
        request = urllib2.Request(url, data, headers)
        try:
            f = self.opener.open(request)
            data = f.read()
            f.close()
        except HTTPError, e:
            data = e.read()
            e.locust_http_response = HttpResponse(url, name, e.code, data, e.info, self.gzip)
            e.close()
            raise e

        return HttpResponse(url, name, f.code, data, f.info, self.gzip)
