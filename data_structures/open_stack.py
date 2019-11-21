class JSONTrace:
    def __init__(self, nodes, edges, request_type):
        self.nodes = nodes
        self.edges = edges
        self.request = request_type


class JSONNode:
    def __init__(self, trace_id, parent_id, tracepoint_id, timestamp, variant):
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.tracepoint_id = tracepoint_id
        self.timestamp = timestamp
        self.variant = variant


class JSONEdge:
    def __init__(self, source, destination, duration, variant):
        self.source = source
        self.destination = destination
        self.duration = duration
        self.variant = variant
