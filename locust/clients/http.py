"""HTTP Locust client"""
import re
import time
import logging
import requests
import six

from pprint import pformat
from requests import Request, Response
from requests.auth import HTTPBasicAuth
from requests.exceptions import (InvalidSchema, InvalidURL, MissingSchema,
                                 RequestException, HTTPError)

from six.moves.urllib.parse import urlparse, urlunparse

from locust import events
from locust.exception import CatchResponseError, ResponseError, RescheduleTask
from locust.log import LazyLog

absolute_http_url_regexp = re.compile(r"^https?://", re.I)
logger = logging.getLogger(__name__)


def fire_success(meta, task):
    events.request_success.fire(
        request_type=meta["method"],
        name=meta["name"],
        response_time=meta["response_time"],
        response_length=meta["content_size"],
        task=task
    )

def fire_failure(meta, task, exception):
    events.request_failure.fire(
        request_type=meta["method"],
        name=meta["name"],
        response_time=meta["response_time"],
        exception=exception,
        task=task
    )   

class LocustResponse(Response):

    def raise_for_status(self):
        if hasattr(self, 'error') and self.error:
            raise self.error
        Response.raise_for_status(self)


class LoggedSession(requests.Session):
    """Wrapper around request.Session, provided addtitional logging capabilities"""

    def request(self, method, url,
                params=None, data=None, headers=None, cookies=None, files=None,
                auth=None, timeout=None, allow_redirects=True, proxies=None,
                hooks=None, stream=None, verify=None, cert=None, json=None):
        """Methods details in requests.Session.request"""
        # Create the Request.
        req = Request(
            method=method.upper(),
            url=url,
            headers=headers,
            files=files,
            data=data or {},
            json=json,
            params=params or {},
            auth=auth,
            cookies=cookies,
            hooks=hooks,
        )
        prep = self.prepare_request(req)

        proxies = proxies or {}

        settings = self.merge_environment_settings(
            prep.url, proxies, stream, verify, cert
        )

        # Send the request.
        send_kwargs = {
            'timeout': timeout,
            'allow_redirects': allow_redirects,
        }
        send_kwargs.update(settings)

        logger.debug(LazyLog(self._format_request, prep, data or json))
        resp = self.send(prep, **send_kwargs)
        logger.debug(LazyLog(self._format_response, resp, method))

        return resp

    def _format_request(self, request, data):
        payload = "  PAYLOAD:\n{}\n".format(pformat(data)) if data else ''
        return "HTTP Request\n" +\
                "  METHOD: {}\n".format(request.method) +\
                "  URL: {}\n".format(request.url) +\
                "  HEADERS: \n{}\n".format("\n".join(
                    ["    {}: {}".format(k, v) for k, v in request.headers.items()]
                )) +\
                payload

    def _format_response(self, response, method):
        data = response.json() if self._is_response_json(response) else response.content
        payload = "  PAYLOAD:\n{}\n".format(pformat(data)) if data else ''
        return "HTTP Response\n" +\
                "  METHOD: {}\n".format(method) +\
                "  URL: {}\n".format(response.url) +\
                "  RESULT CODE: {}\n".format(response.status_code) +\
                "  HEADERS: \n{}\n".format("\n".join(
                    ["    {}: {}".format(k, v) for k, v in response.headers.items()]
                )) +\
                payload

    def _is_response_json(self, response):
        result = False
        flat_headers = {k.lower(): v.lower() for k, v in response.headers.items()}
        if 'json' in flat_headers.get('content-type', ''):
            result = True
        return result


class HttpSession(LoggedSession):
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
    def __init__(self, locust, base_url, *args, **kwargs):
        super(LoggedSession, self).__init__(*args, **kwargs)

        self.base_url = base_url
        self.binded_locust = locust

        # Check for basic authentication
        parsed_url = urlparse(self.base_url)
        if parsed_url.username and parsed_url.password:
            netloc = parsed_url.hostname
            if parsed_url.port:
                netloc += ":%d" % parsed_url.port

            # remove username and password from the base_url
            self.base_url = urlunparse((
                parsed_url.scheme,
                netloc,
                parsed_url.path,
                parsed_url.params,
                parsed_url.query,
                parsed_url.fragment
            ))
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
        :param timeout: (optional) How long to wait for the server to send data before giving up, as a float,
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
        request_meta["start_time"] = time.time()

        response = self._send_request_safe_mode(method, url, **kwargs)

        # record the consumed time
        request_meta["response_time"] = int((time.time() - request_meta["start_time"]) * 1000)
        request_name = (response.history and response.history[0] or response).request.path_url
        request_meta["name"] = name or request_name

        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        if kwargs.get("stream", False):
            request_meta["content_size"] = int(response.headers.get("content-length") or 0)
        else:
            request_meta["content_size"] = len(response.content or "")

        if catch_response:
            response.locust_request_meta = request_meta
            return ResponseContextManager(response, self.binded_locust.current_task)
        else:
            try:
                response.raise_for_status()
            except HTTPError as exception:
                error = exception.message.split('for url:')[0]
                message = "{}for: {} {} ".format(error, method, request_meta["name"])
                exception = exception.__class__(
                    message,
                    request=exception.request,
                    response=exception.response,
                )
                fire_failure(request_meta, self.binded_locust.current_task, exception)
                name = "{} {}".format(request_meta["method"], request_meta["name"])
                raise RescheduleTask(exception, name)
            except RequestException as exception:
                fire_failure(request_meta, self.binded_locust.current_task, exception)
                name = "{} {}".format(request_meta["method"], request_meta["name"])
                raise RescheduleTask(exception, name)
            else:
                fire_success(request_meta, self.binded_locust.current_task)
            return response

    def _send_request_safe_mode(self, method, url, **kwargs):
        """
        Send an HTTP request, and catch any exception that might occur due to connection problems.

        Safe mode has been removed from requests 1.x.
        """
        try:
            return LoggedSession.request(self, method, url, **kwargs)
        except (MissingSchema, InvalidSchema, InvalidURL):
            raise
        except RequestException as exception:
            response = LocustResponse()
            response.error = exception
            response.status_code = 0  # with this status_code, content returns None
            response.request = Request(method, url).prepare()
            return response


class ResponseContextManager(LocustResponse):
    """
    A Response class that also acts as a context manager that provides the ability to manually
    control if an HTTP request should be marked as successful or a failure in Locust's statistics

    This class is a subclass of :py:class:`Response <requests.Response>` with two additional
    methods: :py:meth:`success <locust.clients.ResponseContextManager.success>` and
    :py:meth:`failure <locust.clients.ResponseContextManager.failure>`.
    """

    _is_reported = False

    def __init__(self, response, task):
        # copy data from response to this object
        self.__dict__ = response.__dict__
        self.task = task

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
            except requests.exceptions.RequestException as e:
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
        fire_success(self.locust_request_meta, self.task)
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
        if isinstance(exc, six.string_types):
            exc = CatchResponseError(exc)

        fire_failure(self.locust_request_meta, self.task, exc)
        self._is_reported = True
        name = "{} {}".format(self.locust_request_meta["method"], self.locust_request_meta["name"])
        raise RescheduleTask(exc, name)
