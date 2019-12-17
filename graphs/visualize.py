import os
import time
import random



import networkx as nx



from network_motifs.graphs.construct import ConstructGraphFromTrace



def VisualizeGraphFromTrace(trace):
    """
    Construct a 'dot' file graph for this trace. Each node in the trace gets
    a unique node in the graph with edges indicating parent-child relations.
    Nodes in different node sequences are different colors.
    @param trace: the trace for which to construct a graph
    """
    # get the dataset for this trace
    dataset = trace.dataset

    if not os.path.exists('dots'):
        os.mkdir('dots')
    if not os.path.exists('dots/{}'.format(dataset)):
        os.mkdir('dots/{}'.format(dataset))

    graph = ConstructGraphFromTrace(trace)

    # create a mapping between sequences and colors
    color_options = ['red', 'green', 'blue', 'orange', 'cyan', 'magenta', 'yellow',
                     'dodgerblue', 'turquoise', 'lightcoral', 'pink', 'darkviolet',
                     'darkgreen', 'salmon', 'brown', 'violet', 'darkolivegreen']
    sequences = {}
    sequences[None] = 'black'
    for sequence in trace.sequences:
        sequences[sequence] = random.choice(color_options)

    # add colors to nodes based on sequences
    colors = {}
    for node in trace.nodes:
        colors[node.index] = sequences[node.sequence]

    # set the attributes for this node
    nx.set_node_attributes(graph, colors, 'color')

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('dots/{}/{}.dot'.format(dataset, trace.base_id))

    motifs = {}
    motifs[None] = 'black'
    for motif in trace.motifs:
        motifs[motif] = random.choice(color_options)

    # add colors to nodes based on sequences
    colors = {}
    for node in trace.nodes:
        colors[node.index] = motifs[node.motif]

    # set the attributes for this node
    nx.set_node_attributes(graph, colors, 'color')

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('dots/{}/{}-motifs.dot'.format(dataset, trace.base_id))

    collapsed_motifs = {}
    collapsed_motifs[None] = 'black'
    for collapsed_motif in trace.collapsed_motifs:
        collapsed_motifs[collapsed_motif] = random.choice(color_options)

    # add colors to nodes based on sequences
    colors = {}
    for node in trace.nodes:
        colors[node.index] = collapsed_motifs[node.collapsed_motif]

    # set the attributes for this node
    nx.set_node_attributes(graph, colors, 'color')

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('dots/{}/{}-collapsed-motifs.dot'.format(dataset, trace.base_id))

    fuzzy_collapsed_motifs = {}
    fuzzy_collapsed_motifs[None] = 'black'
    for fuzzy_collapsed_motif in trace.fuzzy_collapsed_motifs:
        fuzzy_collapsed_motifs[fuzzy_collapsed_motif] = random.choice(color_options)

    # add colors to nodes based on sequences
    colors = {}
    for node in trace.nodes:
        colors[node.index] = fuzzy_collapsed_motifs[node.fuzzy_collapsed_motif]

    # set the attributes for this node
    nx.set_node_attributes(graph, colors, 'color')

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('dots/{}/{}-fuzzy-collapsed-motifs.dot'.format(dataset, trace.base_id))



def VisualizeCollapsedGraph(trace, node_names, edges, fuzzy):
    """
    Visualize the collapsed graph and save the output.
    @params trace: the trace for which to visualize a collapsed graph
    @params node_names: names for the collapsed nodes
    @params edges: list of edges connecting the nodes
    """
    # get relavent information for output filename
    dataset = trace.dataset
    base_id = trace.base_id

    if not os.path.exists('dots'):
        os.mkdir('dots')
    if not os.path.exists('dots/{}'.format(dataset)):
        os.mkdir('dots/{}'.format(dataset))

    # create the digraph
    graph = nx.DiGraph()

    for index, name in enumerate(node_names):
        graph.add_node(index, label=name)

    # populate the edges in the graph
    for (source_index, destination_index) in edges:
        graph.add_edge(source_index, destination_index)

    # get the output filename for this collapsed graph
    if fuzzy: output_filename = 'dots/{}/{}-fuzzy-collapsed.dot'.format(dataset, base_id)
    else: output_filename = 'dots/{}/{}-collapsed.dot'.format(dataset, base_id)

    # save the graph into dot format
    A = nx.nx_agraph.to_agraph(graph)
    A.layout('dot')
    A.draw(output_filename)
