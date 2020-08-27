import msgpack


class Message(object):
    def __init__(self, message_type, data, node_id):
        self.type = message_type
        self.data = data
        self.node_id = node_id

    def __repr__(self):
        return "<Message %s:%s>" % (self.type, self.node_id)

    def serialize(self):
        return msgpack.dumps((self.type, self.data, self.node_id))

    @classmethod
    def unserialize(cls, data):
        msg = cls(*msgpack.loads(data, raw=False, strict_map_key=False))
        return msg
