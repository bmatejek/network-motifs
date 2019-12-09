import random



import networkx as nx



def OriginalGraph(dataset, trace):
    """
    Construct a 'dot' file graph for this trace. Each node in the trace gets
    a unique node in the graph with edges indicating parent-child relations.
    Nodes in different node sequences are different colors.
    @param dataset: the dataset name that the trace belongs to
    @param trace: the trace for which to construct a graph
    """
    nodes = trace.nodes
    edges = trace.edges

    # create a directred graph
    graph = nx.DiGraph()

    # each sequence receives a unique coloring
    nsequences = len(trace.sequences)
    colors = ['red', 'green', 'blue', 'orange', 'cyan', 'magenta']
    color_map = []
    for iv in range(nsequences):
        color_map.append(random.choice(colors))

    for index, node in enumerate(nodes):
        if node.sequence == None:
            graph.add_node(index, label=node.Name(), color='black')
        else:
            graph.add_node(index, label=node.Name(), color=color_map[node.sequence.index])

    # populate the edges in the graph
    for edge in edges:
        graph.add_edge(edge.source.index, edge.destination.index)

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('dots/{}/{}.dot'.format(dataset, trace.base_id))



def StackedGraph(dataset, trace):
    """
    Construct a 'dot' file graph for this trace. Each function in the trace gets
    a unique node in the graph with edges indicating parent-child relations.
    One function can occur multiple times in the trace.
    @param dataset: the dataset name that the trace belongs to
    @param trace: the trace for which to construct a graph
    """
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

    # create a list of edges
    edge_list = set()
    for edge in edges:
        source_index = node_name_to_index[edge.source.Name()]
        destination_index = node_name_to_index[edge.destination.Name()]

        edge_list.add((source_index, destination_index))

    for (source_index, destination_index) in edge_list:
        graph.add_edge(source_index, destination_index)

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('graphs/{}/{}.dot'.format(dataset, trace.base_id))
