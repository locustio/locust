from locust import User, events

import time
from typing import Any

from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams


class QdrantLocustClient:
    """Qdrant Client Wrapper"""

    def __init__(self, url, collection_name, api_key=None, timeout=60, **kwargs):
        self.url = url
        self.collection_name = collection_name
        self.api_key = api_key
        self.timeout = timeout

        self.client = QdrantClient(
            url=self.url,
            api_key=self.api_key,
            timeout=self.timeout,
            **kwargs,
        )

    def close(self):
        self.client.close()

    def create_collection(self, vectors_config, **kwargs):
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=vectors_config,
                **kwargs,
            )

    def upsert(self, points):
        start = time.time()
        try:
            result = self.client.upsert(
                collection_name=self.collection_name,
                points=points,
            )
            total_time = (time.time() - start) * 1000
            return {"success": True, "response_time": total_time, "result": result}
        except Exception as e:
            return {
                "success": False,
                "response_time": (time.time() - start) * 1000,
                "exception": e,
            }

    def search(
        self,
        query,
        limit=10,
        query_filter=None,
        search_params=None,
        with_payload=True,
    ):
        start = time.time()
        try:
            result = self.client.query_points(
                collection_name=self.collection_name,
                query=query,
                limit=limit,
                query_filter=query_filter,
                search_params=search_params,
                with_payload=with_payload,
            )
            total_time = (time.time() - start) * 1000
            empty = len(result.points) == 0
            return {
                "success": not empty,
                "response_time": total_time,
                "empty": empty,
                "result": result,
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": (time.time() - start) * 1000,
                "exception": e,
            }

    def scroll(
        self,
        scroll_filter=None,
        limit=10,
        with_payload=True,
    ):
        start = time.time()
        try:
            result, next_offset = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=scroll_filter,
                limit=limit,
                with_payload=with_payload,
            )
            total_time = (time.time() - start) * 1000
            empty = len(result) == 0
            return {
                "success": not empty,
                "response_time": total_time,
                "empty": empty,
                "result": result,
                "next_offset": next_offset,
            }
        except Exception as e:
            return {
                "success": False,
                "response_time": (time.time() - start) * 1000,
                "exception": e,
            }

    def delete(self, points_selector):
        start = time.time()
        try:
            result = self.client.delete(
                collection_name=self.collection_name,
                points_selector=points_selector,
            )
            total_time = (time.time() - start) * 1000
            return {"success": True, "response_time": total_time, "result": result}
        except Exception as e:
            return {
                "success": False,
                "response_time": (time.time() - start) * 1000,
                "exception": e,
            }


# ----------------------------------
# Locust User wrapper
# ----------------------------------


class QdrantUser(User):
    """Locust User implementation for Qdrant operations.

    This class wraps the QdrantLocustClient implementation and translates
    client method results into Locust request events so that performance
    statistics are collected properly.

    Parameters
    ----------
    host : str
        Qdrant server URL, e.g. ``"http://localhost:6333"``.
    collection_name : str
        The name of the collection to operate on.
    ``**client_kwargs``
        Additional keyword arguments forwarded to the client.
    ``**collection_kwargs``
        Additional keyword arguments forwarded to ``create_collection``.
    """

    abstract = True

    url: str = "http://localhost:6333"
    api_key: str | None = None
    collection_name: str | None = None
    timeout: int = 60
    vectors_config: VectorParams | None = None
    client_kwargs: dict | None = None
    collection_kwargs: dict | None = None

    def __init__(self, environment):
        super().__init__(environment)

        if self.collection_name is None:
            raise ValueError("'collection_name' must be provided for QdrantUser")

        self.client_type = "qdrant"
        self.client = QdrantLocustClient(
            url=self.url,
            api_key=self.api_key,
            collection_name=self.collection_name,
            timeout=self.timeout,
            **(self.client_kwargs or {}),
        )
        if self.vectors_config is not None:
            self.client.create_collection(vectors_config=self.vectors_config, **(self.collection_kwargs or {}))

    @staticmethod
    def _fire_event(request_type: str, name: str, result: dict[str, Any]):
        """Emit a Locust request event from a Qdrant client result dict."""
        response_time = int(result.get("response_time", 0))
        events.request.fire(
            request_type=f"{request_type}",
            name=name,
            response_time=response_time,
            response_length=0,
            exception=result.get("exception"),
        )

    def upsert(self, points):
        result = self.client.upsert(points)
        self._fire_event(self.client_type, "upsert", result)
        return result

    def search(
        self,
        query,
        limit=10,
        query_filter=None,
        search_params=None,
        with_payload=True,
    ):
        result = self.client.search(
            query=query,
            limit=limit,
            query_filter=query_filter,
            search_params=search_params,
            with_payload=with_payload,
        )
        self._fire_event(self.client_type, "search", result)
        return result

    def scroll(
        self,
        scroll_filter=None,
        limit=10,
        with_payload=True,
    ):
        result = self.client.scroll(
            scroll_filter=scroll_filter,
            limit=limit,
            with_payload=with_payload,
        )
        self._fire_event(self.client_type, "scroll", result)
        return result

    def delete(self, points_selector):
        result = self.client.delete(points_selector)
        self._fire_event(self.client_type, "delete", result)
        return result

    def on_stop(self):
        self.client.close()
