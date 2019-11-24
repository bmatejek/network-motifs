class OpenStackTrace:
    def __init__(self, nodes, edges, request_type, base_id):
        self.nodes = nodes
        self.edges = edges
        self.request_type = request_type
        self.id_to_node = {}
        self.base_id = base_id

        for node in nodes:
            self.id_to_node[node.trace_id] = node

        # update the parent node references for nodes
        for edge in edges:
            source = edge.source
            destination = edge.destination

            destination.parent_node = source



    def UniqueFunctions(self):
        functions = set()

        for node in self.nodes:
            functions.add(node.tracepoint_id)

        return functions

    def GetNodeFromID(self, trace_id):
        return self.id_to_node[trace_id]



class OpenStackNode:
    def __init__(self, trace_id, parent_id, tracepoint_id, timestamp, variant):
        self.trace_id = trace_id
        self.parent_id = parent_id
        self.tracepoint_id = tracepoint_id
        self.timestamp = timestamp
        self.variant = variant
        # will get updated in OpenStackTrace initializer
        self.parent_node = None



class OpenStackEdge:
    def __init__(self, nodes, source, destination, duration, variant):
        self.source = nodes[source]
        self.destination = nodes[destination]
        self.duration = duration
        self.variant = variant



def GetUniqueFunctions(traces):
    functions = set()

    for trace in traces:
        functions = functions.union(trace.UniqueFunctions())

    return functions
