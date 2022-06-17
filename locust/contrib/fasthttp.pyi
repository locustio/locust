from typing import Any, TypedDict, Union, Optional
from typing_extensions import Unpack

class RequestArgs(TypedDict):
    name: Optional[str]
    catch_response: Optional[bool]
    context: Optional[dict]
    params: Optional[Union[dict, str, bytes]]
    data: Optional[Any]
    headers: Optional[Any]
    cookies: Optional[Any]
    files: Optional[Any]
    auth: Optional[Any]
    timeout: Optional[Any]
    allow_redirects: bool
    proxies: Optional[Any]
    hooks: Optional[Any]
    stream: Optional[Any]
    verify: Optional[Any]
    cert: Optional[Any]
    json: Optional[Any]

class FastHttpSession:
    def request(self, method: str, url: Union[str, bytes], name=None, **kwargs: Unpack[RequestArgs]): ...
    def get(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def options(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def head(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def post(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def put(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def patch(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
    def delete(self, url: Union[str, bytes], **kwargs: Unpack[RequestArgs]): ...
