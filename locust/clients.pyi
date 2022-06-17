import requests
from typing import Any, Union
from typing_extensions import Unpack, TypedDict, NotRequired

class RequestArgs(TypedDict):
    name: NotRequired[str]
    catch_response: NotRequired[bool]
    context: NotRequired[dict]
    params: NotRequired[Any]
    data: NotRequired[Any]
    headers: NotRequired[Any]
    cookies: NotRequired[Any]
    files: NotRequired[Any]
    auth: NotRequired[Any]
    timeout: NotRequired[Any]
    allow_redirects: NotRequired[bool]
    proxies: NotRequired[Any]
    hooks: NotRequired[Any]
    stream: NotRequired[Any]
    verify: NotRequired[Any]
    cert: NotRequired[Any]
    json: NotRequired[Any]

class HttpSession(requests.Session):
    def get(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def options(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def head(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def post(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def put(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def patch(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def delete(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
