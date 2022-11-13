class Message(object):
    def __init__(self, type, qos, topic, payload, start_time, timeout, name):
        self.type = (type,)
        self.qos = (qos,)
        self.topic = topic
        self.payload = payload
        self.start_time = start_time
        self.timeout = timeout
        self.name = name
