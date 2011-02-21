import urllib2
import urllib
from stats import log_request
import base64

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

class HttpBrowser(object):
    """
    Class for performing web requests and holding session cookie between requests (in order
    to be able to log in to websites). 
    
    Logs each request so that locust can display statistics.
    """

    def __init__(self, base_url, basic_auth=None):
        self.base_url = base_url
        handlers = [urllib2.HTTPCookieProcessor()]

        if basic_auth:
            if not isinstance(basic_auth, tuple) or len(basic_auth) != 2:
                print "Invalid basic_auth parameter."
                print "The basic_auth parameter must be a two-tuple (user, password)."
            else:
                user, password = basic_auth
                auth_handler = HttpBasicAuthHandler(user, password)
                handlers.append(auth_handler)

        self.opener = urllib2.build_opener(*handlers)
        urllib2.install_opener(self.opener)
    
    @log_request
    def get(self, path, name=None):
        """
        Make an HTTP GET request.
        
        Arguments:
        
        * *path* is the relative path to request.
        """
        f = self.opener.open(self.base_url + path)
        data = f.read()
        f.close()
        return data
    
    @log_request
    def post(self, path, data, name=None):
        """
        Make an HTTP POST request.
        
        Arguments:
        
        * *path* is the relative path to request.
        * *data* dict with the data that will be sent in the body of the POST request
        
        Example::
        
            client = HttpBrowser("http://example.com")
            client.post("/post", {"user":"joe_hill"})
        """
        f = self.opener.open(self.base_url + path, urllib.urlencode(data))
        data = f.read()
        f.close()
        return data
    