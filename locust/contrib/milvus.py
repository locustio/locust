import gevent.monkey

gevent.monkey.patch_all()
import grpc.experimental.gevent as grpc_gevent

grpc_gevent.init_gevent()

from locust import User, events

import time
from abc import ABC, abstractmethod
from typing import Any

from pymilvus import CollectionSchema, MilvusClient
from pymilvus.milvus_client import IndexParams


class BaseClient(ABC):
    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def create_collection(self, schema, index_params, **kwargs) -> None:
        pass

    @abstractmethod
    def insert(self, data) -> dict[str, Any]:
        pass

    @abstractmethod
    def upsert(self, data) -> dict[str, Any]:
        pass

    @abstractmethod
    def search(
        self,
        data,
        anns_field,
        limit,
        filter="",
        search_params=None,
        output_fields=None,
        calculate_recall=False,
        ground_truth=None,
    ) -> dict[str, Any]:
        pass

    @abstractmethod
    def hybrid_search(self, reqs, ranker, limit, output_fields=None) -> dict[str, Any]:
        pass

    @abstractmethod
    def query(self, filter, output_fields=None) -> dict[str, Any]:
        pass

    @abstractmethod
    def delete(self, filter) -> dict[str, Any]:
        pass


class MilvusV2Client(BaseClient):
    """Milvus v2 Python SDK Client Wrapper"""

    def __init__(self, uri, collection_name, token="root:Milvus", db_name="default", timeout=60):
        self.uri = uri
        self.collection_name = collection_name
        self.token = token
        self.db_name = db_name
        self.timeout = timeout

        # Initialize MilvusClient v2
        self.client = MilvusClient(
            uri=self.uri,
            token=self.token,
            db_name=self.db_name,
            timeout=self.timeout,
        )

    def close(self):
        self.client.close()

    def create_collection(self, schema, index_params, **kwargs):
        self.client.create_collection(
            collection_name=self.collection_name,
            schema=schema,
            index_params=index_params,
            **kwargs,
        )

    def insert(self, data):
        start = time.time()
        try:
            result = self.client.insert(collection_name=self.collection_name, data=data)
            total_time = (time.time() - start) * 1000
            return {"success": True, "response_time": total_time, "result": result}
        except Exception as e:
            return {
                "success": False,
                "response_time": (time.time() - start) * 1000,
                "exception": e,
            }

    def upsert(self, data):
        start = time.time()
        try:
            result = self.client.upsert(collection_name=self.collection_name, data=data)
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
        data,
        anns_field,
        limit,
        filter="",
        search_params=None,
        output_fields=None,
        calculate_recall=False,
        ground_truth=None,
    ):
        if output_fields is None:
            output_fields = ["id"]

        start = time.time()
        try:
            result = self.client.search(
                collection_name=self.collection_name,
                data=data,
                anns_field=anns_field,
                filter=filter,
                limit=limit,
                search_params=search_params,
                output_fields=output_fields,
            )
            total_time = (time.time() - start) * 1000
            empty = len(result) == 0 or all(len(r) == 0 for r in result)

            # Prepare base result
            search_result = {
                "success": not empty,
                "response_time": total_time,
                "empty": empty,
                "result": result,
            }

            # Calculate recall if requested
            if calculate_recall and ground_truth is not None and not empty:
                recall_value = self.get_recall(result, ground_truth, limit)
                search_result["recall"] = recall_value

            return search_result
        except Exception as e:
            return {
                "success": False,
                "response_time": (time.time() - start) * 1000,
                "exception": e,
            }

    def hybrid_search(self, reqs, ranker, limit, output_fields=None):
        if output_fields is None:
            output_fields = ["id"]

        start = time.time()
        try:
            result = self.client.hybrid_search(
                collection_name=self.collection_name,
                reqs=reqs,
                ranker=ranker,
                limit=limit,
                output_fields=output_fields,
                timeout=self.timeout,
            )
            total_time = (time.time() - start) * 1000
            empty = len(result) == 0 or all(len(r) == 0 for r in result)

            # Prepare base result
            search_result = {
                "success": not empty,
                "response_time": total_time,
                "empty": empty,
                "result": result,
            }

            return search_result
        except Exception as e:
            return {
                "success": False,
                "response_time": (time.time() - start) * 1000,
                "exception": e,
            }

    @staticmethod
    def get_recall(search_results, ground_truth, limit=None):
        """Calculate recall for V2 client search results."""
        try:
            # Extract IDs from V2 search results
            retrieved_ids = []
            if isinstance(search_results, list) and len(search_results) > 0:
                # search_results[0] contains the search results for the first query
                for hit in search_results[0] if isinstance(search_results[0], list) else search_results:
                    if isinstance(hit, dict) and "id" in hit:
                        retrieved_ids.append(hit["id"])
                    elif hasattr(hit, "get"):
                        retrieved_ids.append(hit.get("id"))

            # Apply limit if specified
            if limit is None:
                limit = len(retrieved_ids)

            if len(ground_truth) < limit:
                raise ValueError(f"Ground truth length is less than limit: {len(ground_truth)} < {limit}")

            # Calculate recall
            ground_truth_set = set(ground_truth[:limit])
            retrieved_set = set(retrieved_ids)
            intersect = len(ground_truth_set.intersection(retrieved_set))
            return intersect / len(ground_truth_set)

        except Exception:
            return 0.0

    def query(self, filter, output_fields=None):
        if output_fields is None:
            output_fields = ["id"]

        start = time.time()
        try:
            result = self.client.query(
                collection_name=self.collection_name,
                filter=filter,
                output_fields=output_fields,
            )
            total_time = (time.time() - start) * 1000
            empty = len(result) == 0
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

    def delete(self, filter):
        start = time.time()
        try:
            result = self.client.delete(collection_name=self.collection_name, filter=filter)
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


class MilvusUser(User):
    """Locust User implementation for Milvus operations.

    This class wraps the MilvusV2Client implementation and translates
    client method results into Locust request events so that performance
    statistics are collected properly.

    Parameters
    ----------
    host : str
        Milvus server URI, e.g. ``"http://localhost:19530"``.
    collection_name : str
        The name of the collection to operate on.
    **client_kwargs
        Additional keyword arguments forwarded to the client.
    """

    abstract = True

    def __init__(
        self,
        environment,
        uri: str = "http://localhost:19530",
        token: str = "root:Milvus",
        collection_name: str = "test_collection",
        db_name: str = "default",
        timeout: int = 60,
        schema: CollectionSchema | None = None,
        index_params: IndexParams | None = None,
        **kwargs,  # enable_dynamic_field, num_shards, consistency_level etc. ref: https://milvus.io/api-reference/pymilvus/v2.6.x/MilvusClient/Collections/create_collection.md
    ):
        super().__init__(environment)

        if uri is None:
            raise ValueError("'uri' must be provided for MilvusUser")
        if collection_name is None:
            raise ValueError("'collection_name' must be provided for MilvusUser")

        self.client_type = "milvus"
        self.client = MilvusV2Client(
            uri=uri,
            token=token,
            collection_name=collection_name,
            db_name=db_name,
            timeout=timeout,
        )
        if schema is not None:
            self.client.create_collection(schema=schema, index_params=index_params, **kwargs)

    @staticmethod
    def _fire_event(request_type: str, name: str, result: dict[str, Any]):
        """Emit a Locust request event from a Milvus client result dict."""
        response_time = int(result.get("response_time", 0))
        events.request.fire(
            request_type=f"{request_type}",
            name=name,
            response_time=response_time,
            response_length=0,
            exception=result.get("exception"),
        )

    @staticmethod
    def _fire_recall_event(request_type: str, name: str, result: dict[str, Any]):
        """Emit a Locust request event for recall metric using recall value instead of response time."""
        recall_value = result.get("recall", 0.0)
        # Use recall value as response_time for metric display (scaled by 100 for better visualization) percentage
        response_time_as_recall = int(recall_value * 100)
        events.request.fire(
            request_type=f"{request_type}",
            name=name,
            response_time=response_time_as_recall,
            response_length=result.get("retrieved_count", 0),
            exception=result.get("exception"),
        )

    def insert(self, data):
        result = self.client.insert(data)
        self._fire_event(self.client_type, "insert", result)
        return result

    def upsert(self, data):
        result = self.client.upsert(data)
        self._fire_event(self.client_type, "upsert", result)
        return result

    def search(
        self,
        data,
        anns_field,
        limit,
        filter="",
        search_params=None,
        output_fields=None,
        calculate_recall=False,
        ground_truth=None,
    ):
        result = self.client.search(
            data,
            anns_field,
            limit,
            filter=filter,
            search_params=search_params,
            output_fields=output_fields,
            calculate_recall=calculate_recall,
            ground_truth=ground_truth,
        )
        # Fire search event
        self._fire_event(self.client_type, "search", result)

        # Fire recall event if recall was calculated
        if calculate_recall and "recall" in result:
            self._fire_recall_event(self.client_type, "recall", result)

        return result

    def hybrid_search(self, reqs, ranker, limit, output_fields=None):
        result = self.client.hybrid_search(reqs, ranker, limit, output_fields)
        self._fire_event(self.client_type, "hybrid_search", result)
        return result

    def query(self, filter, output_fields=None):
        result = self.client.query(
            filter=filter,
            output_fields=output_fields,
        )
        self._fire_event(self.client_type, "query", result)
        return result

    def delete(self, filter):
        result = self.client.delete(filter)
        self._fire_event(self.client_type, "delete", result)
        return result

    def on_stop(self):
        self.client.close()
