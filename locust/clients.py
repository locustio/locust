import urllib2
import urllib
from stats import log_request
import base64
from urlparse import urlparse, urlunparse

class HTTPClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    @log_request
    def get(self, url, name=None):
        return urllib2.urlopen(self.base_url + url).read()

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
    
    def __init__(self, url, name, code, data, info):
        self.url = url
        self._name = name
        self.code = code
        self.data = data
        self._info = info
    
    @property
    def info(self):
        """
        urllib2 info object containing info about the response
        """
        return self._info()

class HttpBrowser(object):
    """
    Class for performing web requests and holding session cookie between requests (in order
    to be able to log in to websites). 
    
    Logs each request so that locust can display statistics.
    """

    def __init__(self, base_url):
        self.base_url = base_url
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
    
    @log_request
    def get(self, path, headers={}, name=None):
        """
        Make an HTTP GET request.
        
        Arguments:
        
        * *path* is the relative path to request.
        * *headers* is an optional dict with HTTP request headers
        
        Returns an HttpResponse instance, or None if the request failed.
        """
        url = self.base_url + path
        request = urllib2.Request(url, None, headers)
        f = self.opener.open(request)
        data = f.read()
        f.close()
        return HttpResponse(url, name, f.code, data, f.info)
    
    @log_request
    def post(self, path, data, headers={}, with_response_data=False, name=None):
        """
        Make an HTTP POST request.
        
        Arguments:
        
        * *path* is the relative path to request.
        * *data* dict with the data that will be sent in the body of the POST request
        * *headers* is an optional dict with HTTP request headers
        
        Returns an HttpResponse instance, or None if the request failed.
        
        Example::
        
            client = HttpBrowser("http://example.com")
            response = client.post("/post", {"user":"joe_hill"})
        """
        url = self.base_url + path
        request = urllib2.Request(url, urllib.urlencode(data), headers)
        f = self.opener.open(request)
        data = f.read()
        f.close()
        return HttpResponse(url, name, f.code, data, f.info)
    