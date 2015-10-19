import json


class Message(object):
    def __init__(self, message_type, data, node_id):
        self.type = message_type
        self.data = data
        self.node_id = node_id
    
    def serialize(self):
        return json.dumps((self.type, self.data, self.node_id))
    
    @classmethod
    def unserialize(cls, data):
        msg = cls(*json.loads(data))
        return msg
