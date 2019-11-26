import networkx as nx



def OriginalGraph(dataset, trace):
    nodes = trace.nodes
    edges = trace.edges

    # create a directred graph
    graph = nx.DiGraph()

    for index, node in enumerate(nodes):
        graph.add_node(index, label=node.Name())

    for edge in edges:
        graph.add_edge(trace.node_to_index[edge.source], trace.node_to_index[edge.destination])

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('dots/{}/{}.dot'.format(dataset, trace.base_id))



def StackedGraph(dataset, trace):
    nodes = trace.nodes
    edges = trace.edges

    # create a directed graph
    graph = nx.DiGraph()

    # get the list of unique names
    node_names = set()
    for node in nodes:
        node_names.add(node.Name())

    # create the nodes by name and the index mapping
    node_name_to_index = {}
    for index, node_name in enumerate(sorted(list(node_names))):
        graph.add_node(index, label=node_name)
        node_name_to_index[node_name] = index

    for edge in edges:
        source_index = node_name_to_index[edge.source.Name()]
        destination_index = node_name_to_index[edge.destination.Name()]

        graph.add_edge(source_index, destination_index)

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('graphs/{}/{}.dot'.format(dataset, trace.base_id))
