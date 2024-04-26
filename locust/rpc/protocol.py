from __future__ import annotations

import datetime

import msgpack

try:
    from bson import ObjectId
except ImportError:

    class ObjectId:  # type: ignore
        def __init__(self, s):
            raise Exception("You need to install pymongo or at least bson to be able to send/receive ObjectIds")


def decode(obj):
    if "__datetime__" in obj:
        obj = datetime.datetime.strptime(obj["as_str"], "%Y%m%dT%H:%M:%S.%f")
    elif "__ObjectId__" in obj:
        obj = ObjectId(obj["as_str"])
    return obj


def encode(obj):
    if isinstance(obj, datetime.datetime):
        return {"__datetime__": True, "as_str": obj.strftime("%Y%m%dT%H:%M:%S.%f")}
    elif isinstance(obj, ObjectId):
        return {"__ObjectId__": True, "as_str": str(obj)}
    return obj


class Message:
    def __init__(self, message_type, data, node_id):
        self.type = message_type
        self.data = data
        self.node_id = node_id

    def __repr__(self):
        return f"<Message {self.type}:{self.node_id}>"

    def serialize(self):
        return msgpack.dumps((self.type, self.data, self.node_id), default=encode)

    @classmethod
    def unserialize(cls, data):
        msg = cls(*msgpack.loads(data, raw=False, strict_map_key=False, object_hook=decode))
        return msg
