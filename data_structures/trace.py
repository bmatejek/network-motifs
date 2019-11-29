class Trace(object):
    def __init__(self, nodes, edges, request_type, base_id):
        self.nodes = nodes
        self.edges = edges
        self.request_type = request_type
        self.base_id = base_id
        self.node_to_index = {}
        
        # order the nodes by timestamp
        self.ordered_nodes = []

        # populate the helper dictionaries
        for iv, node in enumerate(nodes):
            self.node_to_index[node] = iv
            node.index = iv

        # need this separately since ordering of nodes can change
        for edge in self.edges:
            edge.destination.parent_nodes.append(edge.source)
            edge.source.children_nodes.append(edge.destination)

        # order the nodes
        self.ordered_nodes = sorted(self.nodes, key=lambda x: (x.timestamp, x.index, x.function_id))

        # make sure that the first node is the start of the chain
        assert (len(self.ordered_nodes[0].parent_nodes) == 0)

        # get the total running time for this trace
        self.duration = self.ordered_nodes[-1].timestamp - self.ordered_nodes[0].timestamp
        assert (self.duration > 0)

    def Filename(self):
        # this method needs to be overridden by inherited classes
        assert (False)

    def UniqueFunctions(self):
        functions = set()

        for node in self.nodes:
            functions.add(node.function_id)

        return functions

    def WriteToFile(self):
        # this method needs to be overridden by inherited classes
        assert (False)

    def KthNode(self, k):
        # ignore out of range nodes
        if k < 0: return None
        if k >= len(self.nodes): return None
        # return the nodes at this location
        return self.ordered_nodes[k]



class TraceNode(object):
    def __init__(self, id, function_id, timestamp):
        self.id = id
        self.function_id = function_id
        self.timestamp = timestamp

        # will be updated when creating Trace object
        self.children_nodes = []
        self.parent_nodes = []
        self.index = -1

    def Name(self):
        # this needs to be overridden by inherited classes
        assert (False)



class TraceEdge(object):
    def __init__(self, source, destination, duration):
        self.source = source
        self.destination = destination
        self.duration = duration



def GetUniqueFunctions(traces):
    functions = set()

    for trace in traces:
        functions = functions | trace.UniqueFunctions()

    return functions



def GetUniqueRequestTypes(traces):
    request_types = set()

    for trace in traces:
        request_types.add(trace.request_type)

    return request_types
