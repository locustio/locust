from __future__ import absolute_import

import chardet
import re
import six
import socket
from timeit import default_timer

if six.PY2:
    from cookielib import CookieJar
    class ConnectionRefusedError(Exception):
        # ConnectionRefusedError doesn't exist in python 2, so we'll 
        # define a dummy class to avoid a NameError
        pass
    str = unicode
else:
    from http.cookiejar import CookieJar

from geventhttpclient.useragent import UserAgent, CompatRequest, CompatResponse, ConnectionError

from locust import events
from locust.core import Locust


# Monkey patch geventhttpclient.useragent.CompatRequest so that Cookiejar works with Python >= 3.3
# More info: https://github.com/requests/requests/pull/871
CompatRequest.unverifiable = False


absolute_http_url_regexp = re.compile(r"^https?://", re.I)


class FastHttpLocust(Locust):
    """
    Represents an HTTP "user" which is to be hatched and attack the system that is to be load tested.
    
    The behaviour of this user is defined by the task_set attribute, which should point to a 
    :py:class:`TaskSet <locust.core.TaskSet>` class.
    
    This class creates a *client* attribute on instantiation which is an HTTP client with support 
    for keeping a user session between requests.
    """
    
    client = None
    """
    Instance of HttpSession that is created upon instantiation of Locust. 
    The client support cookies, and therefore keeps the session between HTTP requests.
    """
    
    def __init__(self):
        super(FastHttpLocust, self).__init__()
        if self.host is None:
            raise LocustError("You must specify the base host. Either in the host attribute in the Locust class, or on the command line using the --host option.")
        
        self.client = FastHttpSession(base_url=self.host)


class LocustErrorResponse(object):
    content = None
    def __init__(self, error):
        self.error = error
        self.status_code = 0


class FastHttpSession(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.cookiejar = CookieJar()
        self.client = LocustUserAgent(max_retries=1, cookiejar=self.cookiejar)
    
    def _build_url(self, path):
        """ prepend url with hostname unless it's already an absolute URL """
        if absolute_http_url_regexp.match(path):
            return path
        else:
            return "%s%s" % (self.base_url, path)
    
    def request(self, method, path, name=None, **kwargs):
        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(path)
        
        # store meta data that is used when reporting the request to locust's statistics
        request_meta = {}
        # set up pre_request hook for attaching meta data to the request object
        request_meta["method"] = method
        request_meta["start_time"] = default_timer()
        request_meta["name"] = name or path
        
        try:
            response = self.client.urlopen(url, method=method, **kwargs)
        except (ConnectionError, ConnectionRefusedError, socket.error) as e:
            # record the consumed time
            request_meta["response_time"] = int((default_timer() - request_meta["start_time"]) * 1000)
            events.request_failure.fire(
                request_type=request_meta["method"], 
                name=request_meta["name"], 
                response_time=request_meta["response_time"], 
                exception=e, 
            )
            if hasattr(e, "response"):
                return e.response
            else:
                return LocustErrorResponse(e)
        else:
            # get the length of the content, but if the argument stream is set to True, we take
            # the size from the content-length header, in order to not trigger fetching of the body
            if kwargs.get("stream", False):
                request_meta["content_size"] = int(response.headers.get("content-length") or 0)
            else:
                request_meta["content_size"] = len(response.content or "")
            
            # record the consumed time
            request_meta["response_time"] = int((default_timer() - request_meta["start_time"]) * 1000)
            events.request_success.fire(
                request_type=request_meta["method"],
                name=request_meta["name"],
                response_time=request_meta["response_time"],
                response_length=request_meta["content_size"],
            )
        return response
    
    def delete(self, path, **kwargs):
        return self.request("DELETE", path, **kwargs)
    
    def get(self, path, **kwargs):
        return self.request("GET", path, **kwargs)
    
    def head(self, path, **kwargs):
        return self.request("HEAD", path, **kwargs)
    
    def options(self, path, **kwargs):
        return self.request("OPTIONS", path, **kwargs)
    
    def patch(self, path, data=None, **kwargs):
        """Sends a POST request"""
        return self.request("PATCH", path, payload=data, **kwargs)
    
    def post(self, path, data=None, **kwargs):
        return self.request("POST", path, payload=data, **kwargs)
    
    def put(self, path, data=None, **kwargs):
        return self.request("PUT", path, payload=data, **kwargs)


class FastResponse(CompatResponse):
    @property
    def text(self):
        # Decode unicode from detected encoding.
        try:
            content = str(self.content, self.apparent_encoding, errors='replace')
        except (LookupError, TypeError):
            # A LookupError is raised if the encoding was not found which could
            # indicate a misspelling or similar mistake.
            #
            # A TypeError can be raised if encoding is None
            #
            # Fallback to decode without specifying encoding
            content = str(self.content, errors='replace')
        return content
    
    @property
    def apparent_encoding(self):
        """The apparent encoding, provided by the chardet library."""
        return chardet.detect(self.content)['encoding']


class LocustUserAgent(UserAgent):
    response_type = FastResponse
    
    def _urlopen(self, request):
        """Override _urlopen() in order to make it use the response_type attribute"""
        client = self.clientpool.get_client(request.url_split)
        resp = client.request(request.method, request.url_split.request_uri,
                              body=request.payload, headers=request.headers)
        return self.response_type(resp, request=request, sent_request=resp._sent_request)
