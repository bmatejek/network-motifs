class Trace(object):
    def __init__(self, nodes, edges, request_type, base_id):
        self.nodes = nodes
        self.edges = edges
        self.request_type = request_type
        self.base_id = base_id
        self.node_to_index = {}

        # populate the helper dictionaries
        for iv, node in enumerate(nodes):
            self.node_to_index[node] = iv

        # need this separately since ordering of nodes can change
        for edge in edges:
            edge.source.parent_nodes.append(edge.destination)

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



class TraceNode(object):
    def __init__(self, id, function_id, timestamp):
        self.id = id
        self.function_id = function_id
        self.timestamp = timestamp

        # will be updated when creating Trace object
        self.parent_nodes = []

    def Name(self):
        # this needs to be overridden by inherited classes
        assert (False)

    def ParentNode(self):
        # return the first parent node
        if not len(self.parent_nodes): return None
        else: return self.parent_nodes[0]



class TraceEdge(object):
    def __init__(self, source, destination, duration):
        self.source = source
        self.destination = destination
        self.duration = duration
