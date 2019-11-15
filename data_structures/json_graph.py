class JSONNode:
    def __init__(self, trace_id, function, timestamp, variance):
        self.trace_id = trace_id
        self.function = function
        self.timestamp = timestamp
        self.variance = variance


class JSONEdge:
    def __init__(self, source, destination, duration, variance):
        self.source = source
        self.destination = destination
        self.duration = duration
        self.variance = variance