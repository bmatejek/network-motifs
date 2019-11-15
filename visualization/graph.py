import networkx as nx
import pygraphviz as pgv




# def VisualizeGraph(nodes, edges, filename):
#     # create graph in visualization format
#     graph = pygraphviz.AGraph(directed=True, comment='Network Trace')

#     # add all of the nodes with the function names
#     for index, node in enumerate(nodes):
#         graph.add_node(index)

#         print ('{} {}'.format(index, node.function))

#     # add all of the weighted edges
#     for edge in edges:
#         graph.add_edge(edge[0], edge[1], weight=edges[edge])
    
#     print (graph.string())
#     graph.draw(filename, prog='neato')

def VisualizeGraph(nodes, edges, filename):
    graph = nx.DiGraph()

    with open('{}.txt'.format(filename), 'w') as fd:
        # add all of the nodes with the function names
        for index, node in enumerate(nodes):
            graph.add_node(index)

            fd.write('{} {}\n'.format(index, node.function))

    for edge in edges:
        graph.add_edge(edge[0], edge[1], weight=edges[edge])

    for _, _, d in graph.edges(data=True):
        d['label'] = d.get('weight', '')

    A = nx.nx_agraph.to_agraph(graph)
    A.layout(prog='dot')
    A.draw('{}.dot'.format(filename))