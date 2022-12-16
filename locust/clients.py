from __future__ import annotations
import re
import time
from contextlib import contextmanager
from typing import Generator, Optional
from urllib.parse import urlparse, urlunparse

import requests
from requests import Request, Response
from requests.adapters import HTTPAdapter
from requests.auth import HTTPBasicAuth
from requests.exceptions import InvalidSchema, InvalidURL, MissingSchema, RequestException
from urllib3 import PoolManager

from .exception import CatchResponseError, LocustError, ResponseError

absolute_http_url_regexp = re.compile(r"^https?://", re.I)


class LocustResponse(Response):
    def raise_for_status(self):
        if hasattr(self, "error") and self.error:
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
    from a User class' host attribute.

    Each of the methods for making requests also takes two additional optional arguments which
    are Locust specific and doesn't exist in python-requests. These are:

    :param name: (optional) An argument that can be specified to use as label in Locust's statistics instead of the URL path.
                 This can be used to group different URL's that are requested into a single entry in Locust's statistics.
    :param catch_response: (optional) Boolean argument that, if set, can be used to make a request return a context manager
                           to work as argument to a with statement. This will allow the request to be marked as a fail based on the content of the
                           response, even if the response code is ok (2xx). The opposite also works, one can use catch_response to catch a request
                           and then mark it as successful even if the response code was not (i.e 500 or 404).
    """

    def __init__(self, base_url, request_event, user, *args, pool_manager: Optional[PoolManager] = None, **kwargs):
        super().__init__(*args, **kwargs)

        self.base_url = base_url
        self.request_event = request_event
        self.user = user

        # User can group name, or use the group context manager to gather performance statistics under a specific name
        # This is an alternative to passing in the "name" parameter to the requests function
        self.request_name: Optional[str] = None

        # Check for basic authentication
        parsed_url = urlparse(self.base_url)
        if parsed_url.username and parsed_url.password:
            netloc = parsed_url.hostname
            if parsed_url.port:
                netloc += ":%d" % parsed_url.port

            # remove username and password from the base_url
            self.base_url = urlunparse(
                (parsed_url.scheme, netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment)
            )
            # configure requests to use basic auth
            self.auth = HTTPBasicAuth(parsed_url.username, parsed_url.password)

        self.mount("https://", LocustHttpAdapter(pool_manager=pool_manager))
        self.mount("http://", LocustHttpAdapter(pool_manager=pool_manager))

    def _build_url(self, path):
        """prepend url with hostname unless it's already an absolute URL"""
        if absolute_http_url_regexp.match(path):
            return path
        else:
            return f"{self.base_url}{path}"

    @contextmanager
    def rename_request(self, name: str) -> Generator[None, None, None]:
        """Group requests using the "with" keyword"""

        self.request_name = name
        try:
            yield
        finally:
            self.request_name = None

    def request(self, method, url, name=None, catch_response=False, context={}, **kwargs):
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

        # if group name has been set and no name parameter has been passed in; set the name parameter to group_name
        if self.request_name and not name:
            name = self.request_name

        # prepend url with hostname unless it's already an absolute URL
        url = self._build_url(url)

        start_time = time.time()
        start_perf_counter = time.perf_counter()
        response = self._send_request_safe_mode(method, url, **kwargs)
        response_time = (time.perf_counter() - start_perf_counter) * 1000

        request_before_redirect = (response.history and response.history[0] or response).request
        url = request_before_redirect.url

        if not name:
            name = request_before_redirect.path_url

        if self.user:
            context = {**self.user.context(), **context}

        # store meta data that is used when reporting the request to locust's statistics
        request_meta = {
            "request_type": method,
            "response_time": response_time,
            "name": name,
            "context": context,
            "response": response,
            "exception": None,
            "start_time": start_time,
            "url": url,
        }

        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        if kwargs.get("stream", False):
            request_meta["response_length"] = int(response.headers.get("content-length") or 0)
        else:
            request_meta["response_length"] = len(response.content or b"")

        if catch_response:
            return ResponseContextManager(response, request_event=self.request_event, request_meta=request_meta)
        else:
            with ResponseContextManager(response, request_event=self.request_event, request_meta=request_meta):
                pass
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

    _manual_result: bool | Exception | None = None
    _entered = False

    def __init__(self, response, request_event, request_meta):
        # copy data from response to this object
        self.__dict__ = response.__dict__
        self._request_event = request_event
        self.request_meta = request_meta

    def __enter__(self):
        self._entered = True
        return self

    def __exit__(self, exc, value, traceback):
        # if the user has already manually marked this response as failure or success
        # we can ignore the default behaviour of letting the response code determine the outcome
        if self._manual_result is not None:
            if self._manual_result is True:
                self.request_meta["exception"] = None
            elif isinstance(self._manual_result, Exception):
                self.request_meta["exception"] = self._manual_result
            self._report_request()
            return exc is None

        if exc:
            if isinstance(value, ResponseError):
                self.request_meta["exception"] = value
                self._report_request()
            else:
                # we want other unknown exceptions to be raised
                return False
        else:
            # Since we use the Exception message when grouping failures, in order to not get
            # multiple failure entries for different URLs for the same name argument, we need
            # to temporarily override the response.url attribute
            orig_url = self.url
            self.url = self.request_meta["name"]

            try:
                self.raise_for_status()
            except requests.exceptions.RequestException as e:
                while (
                    isinstance(
                        e,
                        (
                            requests.exceptions.ConnectionError,
                            requests.packages.urllib3.exceptions.ProtocolError,
                            requests.packages.urllib3.exceptions.MaxRetryError,
                            requests.packages.urllib3.exceptions.NewConnectionError,
                        ),
                    )
                    and e.__context__  # Not sure if the above exceptions can ever be the lowest level, but it is good to be sure
                ):
                    e = e.__context__
                self.request_meta["exception"] = e

            self._report_request()
            self.url = orig_url

        return True

    def _report_request(self, exc=None):
        self._request_event.fire(**self.request_meta)

    def success(self):
        """
        Report the response as successful

        Example::

            with self.client.get("/does/not/exist", catch_response=True) as response:
                if response.status_code == 404:
                    response.success()
        """
        if not self._entered:
            raise LocustError(
                "Tried to set status on a request that has not yet been made. Make sure you use a with-block, like this:\n\nwith self.client.request(..., catch_response=True) as response:\n    response.success()"
            )
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
        if not self._entered:
            raise LocustError(
                "Tried to set status on a request that has not yet been made. Make sure you use a with-block, like this:\n\nwith self.client.request(..., catch_response=True) as response:\n    response.failure(...)"
            )
        if not isinstance(exc, Exception):
            exc = CatchResponseError(exc)
        self._manual_result = exc


class LocustHttpAdapter(HTTPAdapter):
    def __init__(self, pool_manager: Optional[PoolManager], *args, **kwargs):
        self.poolmanager = pool_manager
        super().__init__(*args, **kwargs)

    def init_poolmanager(self, *args, **kwargs):
        if self.poolmanager is None:
            super().init_poolmanager(*args, **kwargs)


# Monkey patch Response class to give some guidance
def _success(self):
    raise LocustError(
        "If you want to change the state of the request, you must pass catch_response=True. See http://docs.locust.io/en/stable/writing-a-locustfile.html#validating-responses"
    )


def _failure(self):
    raise LocustError(
        "If you want to change the state of the request, you must pass catch_response=True. See http://docs.locust.io/en/stable/writing-a-locustfile.html#validating-responses"
    )


Response.success = _success
Response.failure = _failure
