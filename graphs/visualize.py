import random



import networkx as nx



from network_motifs.graphs.construct import ConstructGraphFromTrace



def VisualizeGraphFromTrace(dataset, trace):
    """
    Construct a 'dot' file graph for this trace. Each node in the trace gets
    a unique node in the graph with edges indicating parent-child relations.
    Nodes in different node sequences are different colors.
    @param dataset: the dataset name that the trace belongs to
    @param trace: the trace for which to construct a graph
    """
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
