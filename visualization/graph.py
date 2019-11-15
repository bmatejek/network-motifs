import pygraphviz


def VisualizeGraph(nodes, edges):
    # create graph in visualization format
    graph = pygraphviz.AGraph(directed=True, comment='Network Trace')

    # add all of the nodes with the function names
    for index, node in enumerate(nodes):
        graph.add_node(index)

    # add all of the weighted edges
    for edge in edges:
        graph.add_edge(edge[0], edge[1], weight=edges[edge])
    
    print (graph.string())
    graph.draw('simple.png', prog='dot')

    pass