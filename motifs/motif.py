class SubGraph(object):
    def __init__(self, vertices, edges):
        self.vertices = vertices
        self.edges = edges



class Motif(object):
    def __init__(self, trace, nodes, motif_index):
        """
        Initialize a motif obejct for a trace and a given set of nodes. A motif
        is a frequently occuring set of nodes that appear in a graph.
        @params trace: the trace corresponding to this motif
        @params nodes: a list of nodes belonging to this motif
        @params motif_index: a unique identifier for this particular subgraph type
        """
        self.trace = trace
        self.nodes = nodes
        self.motif_index = motif_index

        # find the minimum and maximum timestamp for this motif
        self.minimum_timestamp = self.nodes[0].timestamp
        self.maximum_timestamp = self.nodes[0].timestamp
        for node in self.nodes:
            if node.timestamp < self.minimum_timestamp:
                self.minimum_timestamp = node.timestamp
            if node.timestamp > self.maximum_timestamp:
                self.maximum_timestamp = node.timestamp

        # get the duration for this motif
        self.duration = self.maximum_timestamp - self.minimum_timestamp
