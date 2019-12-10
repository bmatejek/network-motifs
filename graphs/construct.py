import networkx as nx



def ConstructGraphFromTrace(trace):
    """
    Construct a networkx graph from this trace using the nodes and edges.
    @param trace: the trace for which to construct a graph
    """
    nodes = trace.nodes
    edges = trace.edges

    # create a directred graph
    graph = nx.DiGraph()

    for index, node in enumerate(nodes):
        graph.add_node(index, label=node.Name())

    # populate the edges in the graph
    for edge in edges:
        graph.add_edge(edge.source.index, edge.destination.index)

    return graph
