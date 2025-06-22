from __future__ import annotations

from locust.env import Environment
from locust.exception import CatchResponseError, LocustError, ResponseError
from locust.user import User
from locust.util.deprecation import DeprecatedFastHttpLocustClass as FastHttpLocust  # noqa: F401

import json
import json as unshadowed_json  # some methods take a named parameter called json
import re
import socket
import time
import traceback
from base64 import b64encode
from contextlib import contextmanager
from http.cookiejar import CookieJar
from json.decoder import JSONDecodeError
from ssl import SSLError
from typing import TYPE_CHECKING, cast
from urllib.parse import urlparse, urlunparse

import gevent
from charset_normalizer import detect
from gevent.timeout import Timeout
from geventhttpclient._parser import HTTPParseError
from geventhttpclient.client import HTTPClientPool
from geventhttpclient.header import Headers
from geventhttpclient.response import HTTPConnectionClosed, HTTPSocketPoolResponse
from geventhttpclient.useragent import CompatRequest, CompatResponse, ConnectionError, UserAgent

# borrow requests's content-type header parsing
from requests.utils import get_encoding_from_headers

if TYPE_CHECKING:
    import sys
    from collections.abc import Callable, Generator
    from typing import Any, TypedDict

    if sys.version_info >= (3, 11):
        from typing import Unpack
    else:
        from typing_extensions import Unpack

    class PostKwargs(TypedDict, total=False):
        name: str | None
        catch_response: bool
        stream: bool
        headers: dict | None
        auth: tuple[str | bytes, str | bytes] | None
        allow_redirects: bool
        context: dict
        params: dict | None
        files: dict | None

    class PutKwargs(PostKwargs, total=False):
        json: Any

    class PatchKwargs(PostKwargs, total=False):
        json: Any

    class RESTKwargs(PostKwargs, total=False):
        data: str | dict | None
        json: Any


# Monkey patch geventhttpclient.useragent.CompatRequest so that Cookiejar works with Python >= 3.3
# More info: https://github.com/requests/requests/pull/871
CompatRequest.unverifiable = False

# Workaround for AttributeError: 'CompatRequest' object has no attribute 'type' in Cookiejar
# https://github.com/locustio/locust/issues/1138
# Might allow secure cookies over non-secure connections but that is a minor concern in a load testing tool
CompatRequest.type = "https"

# Regexp for checking if an absolute URL was specified
absolute_http_url_regexp = re.compile(r"^https?://", re.I)

# List of exceptions that can be raised by geventhttpclient when sending an HTTP request,
# and that should result in a Locust failure
FAILURE_EXCEPTIONS = (
    ConnectionError,
    ConnectionRefusedError,
    ConnectionResetError,
    socket.error,
    SSLError,
    Timeout,
    HTTPConnectionClosed,
)


def _construct_basic_auth_str(username, password):
    """Construct Authorization header value to be used in HTTP Basic Auth"""
    if isinstance(username, str):
        username = username.encode("latin1")
    if isinstance(password, str):
        password = password.encode("latin1")
    return "Basic " + b64encode(b":".join((username, password))).strip().decode("ascii")


def insecure_ssl_context_factory():
    return gevent.ssl._create_unverified_context()


class FastHttpSession:
    auth_header = None

    def __init__(
        self,
        environment: Environment,
        base_url: str,
        user: User | None,
        insecure=True,
        client_pool: HTTPClientPool | None = None,
        ssl_context_factory: Callable | None = None,
        **kwargs,
    ) -> None:
        self.environment = environment
        self.base_url = base_url
        self.cookiejar = CookieJar()
        self.user = user
        if not ssl_context_factory:
            if insecure:
                ssl_context_factory = insecure_ssl_context_factory
            else:
                ssl_context_factory = gevent.ssl.create_default_context
        self.client = LocustUserAgent(
            cookiejar=self.cookiejar,
            ssl_context_factory=ssl_context_factory,
            insecure=insecure,
            client_pool=client_pool,
            **kwargs,
        )

        # Check for basic authentication
        parsed_url = urlparse(self.base_url)
        if parsed_url.username and parsed_url.password:
            netloc = parsed_url.hostname or ""
            if parsed_url.port:
                netloc += ":%d" % parsed_url.port

            # remove username and password from the base_url
            self.base_url = urlunparse(
                (parsed_url.scheme, netloc, parsed_url.path, parsed_url.params, parsed_url.query, parsed_url.fragment)
            )
            # store authentication header (we construct this by using _basic_auth_str() function from requests.auth)
            self.auth_header = _construct_basic_auth_str(parsed_url.username, parsed_url.password)

    def _build_url(self, path: str) -> str:
        """prepend url with hostname unless it's already an absolute URL"""
        if absolute_http_url_regexp.match(path):
            return path
        else:
            return f"{self.base_url}{path}"

    def _send_request_safe_mode(self, method: str, url: str, **kwargs):
        """
        Send an HTTP request, and catch any exception that might occur due to either
        connection problems, or invalid HTTP status codes
        """
        try:
            return self.client.urlopen(url, method=method, **kwargs)
        except FAILURE_EXCEPTIONS as e:
            if hasattr(e, "response"):
                r = e.response
            else:
                req = self.client._make_request(
                    url,
                    method=method,
                    headers=kwargs.get("headers"),
                    payload=kwargs.get("payload"),
                    params=kwargs.get("params"),
                )
                r = ErrorResponse(url=url, request=req)
            r.error = e
            return r

    def request(
        self,
        method: str,
        url: str,
        name: str | None = None,
        data: str | dict | None = None,
        catch_response: bool = False,
        stream: bool = False,
        headers: dict | None = None,
        auth: tuple[str | bytes, str | bytes] | None = None,
        json: Any = None,
        allow_redirects: bool = True,
        context: dict = {},
        **kwargs,
    ) -> ResponseContextManager | FastResponse:
        """
        Send and HTTP request
        Returns :py:class:`locust.contrib.fasthttp.FastResponse` object.

        :param method: method for the new :class:`Request` object.
        :param url: path that will be concatenated with the base host URL that has been specified.
            Can also be a full URL, in which case the full URL will be requested, and the base host
            is ignored.
        :param name: (optional) An argument that can be specified to use as label in Locust's
            statistics instead of the URL path. This can be used to group different URL's
            that are requested into a single entry in Locust's statistics.
        :param catch_response: (optional) Boolean argument that, if set, can be used to make a request
            return a context manager to work as argument to a with statement. This will allow the
            request to be marked as a fail based on the content of the response, even if the response
            code is ok (2xx). The opposite also works, one can use catch_response to catch a request
            and then mark it as successful even if the response code was not (i.e. 500 or 404).
        :param data: (optional) String/bytes to send in the body of the request.
        :param json: (optional) Json to send in the body of the request.
            Automatically sets Content-Type and Accept headers to "application/json".
            Only used if data is not set.
        :param headers: (optional) Dictionary of HTTP Headers to send with the request.
        :param auth: (optional) Auth (username, password) tuple to enable Basic HTTP Auth.
        :param stream: (optional) If set to true the response body will not be consumed immediately
            and can instead be consumed by accessing the stream attribute on the Response object.
            Another side effect of setting stream to True is that the time for downloading the response
            content will not be accounted for in the request time that is reported by Locust.
        :param allow_redirects: (optional) Set to True by default.
        """
        # prepend url with hostname unless it's already an absolute URL
        built_url = self._build_url(url)

        start_time = time.time()  # seconds since epoch

        if self.user:
            context = {**self.user.context(), **context}

        headers = headers or {}
        if auth:
            headers["Authorization"] = _construct_basic_auth_str(auth[0], auth[1])
        elif self.auth_header:
            headers["Authorization"] = self.auth_header
        if "Accept-Encoding" not in headers and "accept-encoding" not in headers:
            headers["Accept-Encoding"] = "gzip, deflate, br, zstd"

        if not data and json is not None:
            data = unshadowed_json.dumps(json)
            if "Content-Type" not in headers and "content-type" not in headers:
                headers["Content-Type"] = "application/json"
            if "Accept" not in headers and "accept" not in headers:
                headers["Accept"] = "application/json"

        if not allow_redirects:
            old_redirect_response_codes = self.client.redirect_resonse_codes
            self.client.redirect_resonse_codes = []

        start_perf_counter = time.perf_counter()
        # send request, and catch any exceptions
        response = self._send_request_safe_mode(method, built_url, payload=data, headers=headers, **kwargs)
        request_meta = {
            "request_type": method,
            "name": name or url,
            "context": context,
            "response": response,
            "exception": None,
            "start_time": start_time,
            "url": built_url,  # this is a small deviation from HttpSession, which gets the final (possibly redirected) URL
        }

        if not allow_redirects:
            self.client.redirect_resonse_codes = old_redirect_response_codes

        request_meta["response_length"] = 0  # default value, if length cannot be determined

        # get the length of the content, but if the argument stream is set to True, we take
        # the size from the content-length header, in order to not trigger fetching of the body
        if stream:
            if response.headers and "response_length" in response.headers:
                request_meta["response_length"] = int(response.headers["response_length"])
        else:
            try:
                request_meta["response_length"] = len(response.content) if response.content else 0
            except HTTPParseError as e:
                request_meta["response_time"] = (time.perf_counter() - start_perf_counter) * 1000
                request_meta["exception"] = e
                self.environment.events.request.fire(**request_meta)
                return response

        # Record the consumed time
        # Note: This is intentionally placed after we record the content_size above, since
        # we'll then trigger fetching of the body (unless stream=True)
        request_meta["response_time"] = (time.perf_counter() - start_perf_counter) * 1000

        if catch_response:
            return ResponseContextManager(response, environment=self.environment, request_meta=request_meta)
        else:
            try:
                response.raise_for_status()
            except FAILURE_EXCEPTIONS as e:
                request_meta["exception"] = e

            self.environment.events.request.fire(**request_meta)
            return response

    def delete(self, url: str, **kwargs: Unpack[RESTKwargs]) -> ResponseContextManager | FastResponse:
        """Sends a DELETE request"""
        return self.request("DELETE", url, **kwargs)

    def get(self, url: str, **kwargs: Unpack[RESTKwargs]) -> ResponseContextManager | FastResponse:
        """Sends a GET request"""
        return self.request("GET", url, **kwargs)

    def iter_lines(self, url: str, method: str = "GET", **kwargs) -> Generator[str]:
        """Sends a iter_lines request"""
        response = self.request(method, url, stream=True, **kwargs)
        response.raise_for_status()
        buffer = ""
        for chunk in response.iter_content(chunk_size=1024, decode_content=True):
            buffer += chunk.decode("utf-8")
            while "\n" in buffer:
                line, buffer = buffer.split("\n", 1)
                yield line

    def head(self, url: str, **kwargs: Unpack[RESTKwargs]) -> ResponseContextManager | FastResponse:
        """Sends a HEAD request"""
        return self.request("HEAD", url, **kwargs)

    def options(self, url: str, **kwargs: Unpack[RESTKwargs]) -> ResponseContextManager | FastResponse:
        """Sends a OPTIONS request"""
        return self.request("OPTIONS", url, **kwargs)

    def patch(
        self, url: str, data: str | dict | None = None, **kwargs: Unpack[PatchKwargs]
    ) -> ResponseContextManager | FastResponse:
        """Sends a PATCH request"""
        return self.request("PATCH", url, data=data, **kwargs)

    def post(
        self, url: str, data: str | dict | None = None, json: Any = None, **kwargs: Unpack[PostKwargs]
    ) -> ResponseContextManager | FastResponse:
        """Sends a POST request"""
        return self.request("POST", url, data=data, json=json, **kwargs)

    def put(
        self, url: str, data: str | dict | None = None, **kwargs: Unpack[PutKwargs]
    ) -> ResponseContextManager | FastResponse:
        """Sends a PUT request"""
        return self.request("PUT", url, data=data, **kwargs)


class FastHttpUser(User):
    """
    FastHttpUser provides the same API as HttpUser, but uses geventhttpclient instead of python-requests
    as its underlying client. It uses considerably less CPU on the load generator, and should work
    as a simple drop-in-replacement in most cases.
    """

    # Below are various UserAgent settings. Change these in your subclass to alter FastHttpUser's behaviour.
    # It needs to be done before FastHttpUser is instantiated, changing them later will have no effect

    network_timeout: float = 60.0
    """Parameter passed to FastHttpSession"""

    connection_timeout: float = 60.0
    """Parameter passed to FastHttpSession"""

    max_redirects: int = 30
    """Parameter passed to FastHttpSession."""

    max_retries: int = 0
    """Parameter passed to FastHttpSession."""

    insecure: bool = True
    """Parameter passed to FastHttpSession. Default True, meaning no SSL verification."""

    default_headers: dict | None = None
    """Parameter passed to FastHttpSession. Adds the listed headers to every request."""

    concurrency: int = 10
    """Parameter passed to FastHttpSession. Describes number of concurrent requests allowed by the FastHttpSession. Default 10.
    Note that setting this value has no effect when custom client_pool was given, and you need to spawn a your own gevent pool
    to use it (as Users only have one greenlet). See test_fasthttp.py / test_client_pool_concurrency for an example."""

    proxy_host: str | None = None
    """Parameter passed to FastHttpSession"""

    proxy_port: int | None = None
    """Parameter passed to FastHttpSession"""

    client_pool: HTTPClientPool | None = None
    """HTTP client pool to use. If not given, a new pool is created per single user."""

    ssl_context_factory: Callable | None = None
    """A callable that return a SSLContext for overriding the default context created by the FastHttpSession."""

    abstract = True
    """Dont register this as a User class that can be run by itself"""

    _callstack_regex = re.compile(r'  File "(\/.[^"]*)", line (\d*),(.*)')

    def __init__(self, environment) -> None:
        super().__init__(environment)
        if self.host is None:
            raise LocustError(
                "You must specify the base host. Either in the host attribute in the User class, or on the command line using the --host option."
            )

        self.client: FastHttpSession = FastHttpSession(
            self.environment,
            base_url=self.host,
            network_timeout=self.network_timeout,
            connection_timeout=self.connection_timeout,
            max_redirects=self.max_redirects,
            max_retries=self.max_retries,
            insecure=self.insecure,
            concurrency=self.concurrency,
            user=self,
            client_pool=self.client_pool,
            ssl_context_factory=self.ssl_context_factory,
            headers=self.default_headers,
            proxy_host=self.proxy_host,
            proxy_port=self.proxy_port,
        )
        """
        Instance of HttpSession that is created upon instantiation of User.
        The client support cookies, and therefore keeps the session between HTTP requests.
        """

    @contextmanager
    def rest(self, method, url, headers: dict | None = None, **kwargs) -> Generator[RestResponseContextManager]:
        """
        A wrapper for self.client.request that:

        * Parses the JSON response to a dict called ``js`` in the response object. Marks the request as failed if the response was not valid JSON.
        * Defaults ``Content-Type`` and ``Accept`` headers to ``application/json``
        * Sets ``catch_response=True`` (so always use a :ref:`with-block <catch-response>`)
        * Catches any unhandled exceptions thrown inside your with-block, marking the sample as failed (instead of exiting the task immediately without even firing the request event)
        """
        headers = headers or {}
        if not ("Content-Type" in headers or "content-type" in headers):
            headers["Content-Type"] = "application/json"
        if not ("Accept" in headers or "accept" in headers):
            headers["Accept"] = "application/json"
        with self.client.request(method, url, catch_response=True, headers=headers, **kwargs) as r:
            resp = cast(RestResponseContextManager, r)
            resp.js = None  # type: ignore
            if resp.content is None:
                resp.failure(str(resp.error))
            elif resp.text:
                try:
                    resp.js = resp.json()
                except JSONDecodeError as e:
                    resp.failure(
                        f"Could not parse response as JSON. {resp.text[:250]}, response code {resp.status_code}, error {e}"
                    )
            try:
                yield resp
            except AssertionError as e:
                if e.args:
                    if e.args[0].endswith(","):
                        short_resp = resp.text[:200] if resp.text else resp.text
                        resp.failure(f"{e.args[0][:-1]}, response was {short_resp}")
                    else:
                        resp.failure(e.args[0])
                else:
                    resp.failure("Assertion failed")

            except Exception as e:
                error_lines = []
                for l in traceback.format_exc().split("\n"):
                    if m := self._callstack_regex.match(l):
                        filename = re.sub(r"/((home|Users)/\w*)/", "~/", m.group(1))
                        error_lines.append(filename + ":" + m.group(2) + m.group(3))
                    short_resp = resp.text[:200] if resp.text else resp.text
                    resp.failure(f"{e.__class__.__name__}: {e} at {', '.join(error_lines)}. Response was {short_resp}")

    @contextmanager
    def rest_(self, method, url, name=None, **kwargs) -> Generator[RestResponseContextManager]:
        """
        Some REST api:s use a timestamp as part of their query string (mainly to break through caches).
        This is a convenience method for that, appending a _=<timestamp> parameter automatically
        """
        separator = "&" if "?" in url else "?"
        if name is None:
            name = url + separator + "_=..."
        with self.rest(method, f"{url}{separator}_={int(time.time() * 1000)}", name=name, **kwargs) as resp:
            yield resp


class FastRequest(CompatRequest):
    payload: str | None = None

    @property
    def body(self) -> str | None:
        return self.payload


class FastResponse(CompatResponse):
    headers: Headers | None = None
    """Dict like object containing the response headers"""

    _response: HTTPSocketPoolResponse | None = None

    encoding: str | float | None = None
    """In some cases setting the encoding explicitly is needed. If so, do it before calling .text"""

    request: FastRequest | None = None

    def __init__(
        self,
        ghc_response: HTTPSocketPoolResponse,
        request: FastRequest | None = None,
        sent_request: str | None = None,
    ):
        super().__init__(ghc_response, request, sent_request)

        self.request = request

    @property
    def text(self) -> str | None:
        """
        Returns the text content of the response as a decoded string
        """
        if self.content is None:
            return None
        if self.encoding is None:
            if self.headers is None:
                # No information, try to detect
                self.encoding = detect(self.content)["encoding"]
            else:
                self.encoding = get_encoding_from_headers(self.headers)
                # No information, try to detect
                if not self.encoding:
                    self.encoding = detect(self.content)["encoding"]
        if self.encoding is None:
            return None
        return str(self.content, str(self.encoding), errors="replace")

    @property
    def url(self) -> str | None:
        """
        Get "response" URL, which is the same as the request URL. This is a small deviation from HttpSession, which gets the final (possibly redirected) URL.
        """
        if self.request is not None:
            return self.request.url

        return None

    def json(self) -> dict:
        """
        Parses the response as json and returns a dict
        """
        return json.loads(self.text)  # type: ignore

    def raise_for_status(self):
        """Raise any connection errors that occurred during the request"""
        if hasattr(self, "error") and self.error:
            raise self.error

    @property
    def status_code(self) -> int:
        """
        We override status_code in order to return None if no valid response was
        returned. E.g. in the case of connection errors
        """
        return self._response.get_code() if self._response is not None else 0

    @property
    def ok(self):
        """Returns True if :attr:`status_code` is less than 400, False if not."""
        return self.status_code < 400

    def _content(self):
        if self.headers is None:
            return None
        return super()._content()

    def success(self):
        raise LocustError(
            "If you want to change the state of the request, you must pass catch_response=True. See http://docs.locust.io/en/stable/writing-a-locustfile.html#validating-responses"
        )

    def failure(self, *_args, **_kwargs):
        raise LocustError(
            "If you want to change the state of the request, you must pass catch_response=True. See http://docs.locust.io/en/stable/writing-a-locustfile.html#validating-responses"
        )


class ErrorResponse:
    """
    This is used as a dummy response object when geventhttpclient raises an error
    that doesn't have a real Response object attached. E.g. a socket error or similar
    """

    headers: Headers | None = None
    content = None
    status_code = 0
    error: Exception | None = None
    text: str | None = None
    request: CompatRequest

    def __init__(self, url: str, request: CompatRequest):
        self.url = url
        self.request = request

    def raise_for_status(self):
        raise self.error


class LocustBadStatusCode(ConnectionError):
    def __repr__(self):
        repr_str = super().__repr__()
        if self.kw_text:
            return repr_str.replace(repr(self.url) + ", ", "")
        return repr_str


class LocustUserAgent(UserAgent):
    response_type = FastResponse
    request_type = FastRequest
    valid_response_codes = frozenset([200, 201, 202, 203, 204, 205, 206, 207, 208, 226, 301, 302, 303, 304, 307])

    def __init__(self, client_pool: HTTPClientPool | None = None, **kwargs):
        super().__init__(**kwargs)

        if client_pool is not None:
            self.clientpool = client_pool

    def _urlopen(self, request):
        """Override _urlopen() in order to make it use the response_type attribute"""
        client = self.clientpool.get_client(request.url_split)
        resp = client.request(
            request.method, request.url_split.request_uri, body=request.payload, headers=request.headers
        )
        return self.response_type(resp, request=request, sent_request=resp._sent_request)

    def _verify_status(self, status_code, url=None):
        """Hook for subclassing"""
        if status_code not in self.valid_response_codes:
            raise LocustBadStatusCode(url, code=status_code)


class ResponseContextManager(FastResponse):
    """
    A Response class that also acts as a context manager that provides the ability to manually
    control if an HTTP request should be marked as successful or a failure in Locust's statistics

    This class is a subclass of :py:class:`FastResponse <locust.contrib.fasthttp.FastResponse>`
    with two additional methods: :py:meth:`success <locust.contrib.fasthttp.ResponseContextManager.success>`
    and :py:meth:`failure <locust.contrib.fasthttp.ResponseContextManager.failure>`.
    """

    _manual_result = None
    _entered = False

    def __init__(self, response, environment, request_meta):
        # copy data from response to this object
        self.__dict__ = response.__dict__
        try:
            self._cached_content = response._cached_content
        except AttributeError:
            pass
        # store reference to locust Environment
        self._environment = environment
        self.request_meta = request_meta

    def __enter__(self):
        self._entered = True
        return self

    def __exit__(self, exc, value, traceback):
        # if the user has already manually marked this response as failure or success
        # we can ignore the default behaviour of letting the response code determine the outcome
        if self._manual_result is not None:
            if self._manual_result is True:
                self._report_request()
            elif isinstance(self._manual_result, Exception):
                self.request_meta["exception"] = self._manual_result
                self._report_request()

            return exc is None

        if exc:
            if isinstance(value, ResponseError):
                self.request_meta["exception"] = value
                self._report_request()
            else:
                return False
        else:
            try:
                self.raise_for_status()
            except FAILURE_EXCEPTIONS as e:
                self.request_meta["exception"] = e
            self._report_request()

        return True

    def _report_request(self):
        self._environment.events.request.fire(**self.request_meta)

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
                if response.content == "":
                    response.failure("No data")
        """
        if not self._entered:
            raise LocustError(
                "Tried to set status on a request that has not yet been made. Make sure you use a with-block, like this:\n\nwith self.client.request(..., catch_response=True) as response:\n    response.failure(...)"
            )
        if not isinstance(exc, Exception):
            exc = CatchResponseError(exc)
        self._manual_result = exc


class RestResponseContextManager(ResponseContextManager):
    js: dict  # This is technically an Optional, but I dont want to force everyone to check it
    error: Exception  # This one too
    headers: Headers  # .. and this one
