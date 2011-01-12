import urllib2
from stats import log_request

class HTTPClient(object):
    def __init__(self, base_url):
        self.base_url = base_url

    @log_request
    def get(self, url, name=None):
        return urllib2.urlopen(self.base_url + url).read()


class HttpBrowser(object):
    def __init__(self, base_url):
        self.base_url = base_url
        self.opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
        urllib2.install_opener(self.opener)
    
    @log_request
    def get(self, url, name=None):
        f = self.opener.open(self.base_url + url)
        data = f.read()
        f.close()
        return data
    
    @log_request
    def post(self, url, data, name=None):
        f = self.opener.open(self.base_url + url, data)
        data = f.read()
        f.close()
        return data
    