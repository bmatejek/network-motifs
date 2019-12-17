import os
import time



import graph_tool.all as gt



from network_motifs.transforms.convert import ConvertTrace2GraphTool, ConvertSubGraph2GraphTool, ConvertCollapsedGraph2GraphTool
from network_motifs.motifs.motif import Motif, SubGraph, WriteMotifs
from network_motifs.utilities.dataIO import ReadTraces



def IdentifyFrequentSubgraphs(dataset, request_type, collapsed, fuzzy):
    """
    Populate an array of frequent subgraphs found using the GASTON algorithm.
    @params dataset: the dataset to mine for frequent sub graphs
    @params request_type: the request type for this set of traces
    """
    # create a list of subgraphs to mine for
    subgraphs = []

    # read the subgraphs generated from GASTON
    if not collapsed: subgraph_filename = 'motifs/patterns/{}/{}-gaston-patterns.txt'.format(dataset, request_type)
    elif fuzzy: subgraph_filename = 'motifs/patterns/{}/{}-fuzzy-collapsed-gaston-patterns.txt'.format(dataset, request_type)
    else: subgraph_filename = 'motifs/patterns/{}/{}-collapsed-gaston-patterns.txt'.format(dataset, request_type)

    with open(subgraph_filename, 'r') as fd:
        # read all of the lines in the file
        lines = fd.readlines()

        # keep track of vertices and edges for each subgraph
        vertices = []
        edges = []

        # parse the graph
        for line in lines:
            # this indicates the start of a new subgraph
            if line[0] == '#' and len(vertices) and len(edges):
                subgraphs.append(SubGraph(vertices, edges))
                # reset the vertices and edges arrays
                vertices = []
                edges = []
            # skip the subgraph counter
            elif line[0] == 't': continue
            # add this vertex to the list of vertices
            elif line[0] == 'v':
                _, vertex_id, vertex_label = line.split()
                vertex_id = int(vertex_id.strip())
                vertex_label = int(vertex_label.strip())
                vertices.append((vertex_id, vertex_label))
            # add this edge to the list of edges
            elif line[0] == 'e':
                _, source_index, destination_index, _ = line.split()
                source_index = int(source_index.strip())
                destination_index = int(destination_index.strip())
                edges.append((source_index, destination_index))

    return subgraphs



def QueryTraces(dataset, request_type):
    """
    Find all occurrences for each motif for this dataset/request_type comboination.
    @params dataset: the dataset to mine for frequent sub graphs
    @params request_type: the request type for this set of traces
    """
    # create the directory structure
    if not os.path.exists('motifs'):
        os.mkdir('motifs')
    if not os.path.exists('motifs/subgraphs'):
        os.mkdir('motifs/subgraphs')
    if not os.path.exists('motifs/subgraphs/{}'.format(dataset)):
        os.mkdir('motifs/subgraphs/{}'.format(dataset))

    # start statistics
    start_time = time.time()

    # read the frequent subgraphs for this dataset/request type
    subgraphs = IdentifyFrequentSubgraphs(dataset, request_type, False, False)

    # read all of the traces and mine the graph
    traces = ReadTraces(dataset, request_type, None)

    for trace in traces:
        # start statistics
        start_time = time.time()

        graph = ConvertTrace2GraphTool(dataset, trace)
        motifs = []

        for motif_index, subgraph in enumerate(subgraphs):
            motif = ConvertSubGraph2GraphTool(subgraph)

            # use graph tool to find all motif occurrences
            vertex_maps = gt.subgraph_isomorphism(motif, graph, vertex_label=(motif.vp.label, graph.vp.label))

            # go through all of the found motif patterns
            for vertex_map in vertex_maps:
                nodes = []
                for node in vertex_map:
                    nodes.append(trace.nodes[node])
                motifs.append(Motif(trace, nodes, motif_index))

        # write the motifs to disk
        output_filename = 'motifs/subgraphs/{}/{}-motifs-complete.motifs'.format(dataset, trace.base_id)
        WriteMotifs(output_filename, motifs)

        # print statistics
        print ('Mined traces for {} in {:0.2f} seconds.'.format(trace.base_id, time.time() - start_time))



def QueryCollapsedGraphs(dataset, request_type, fuzzy):
    """
    Find motifs in the graphs with collapsed node sequences. Saves the motifs to
    file
    @params dataset: dataset to find motifs in the collapsed sequences
    @params request_type: request for this particular set of traces
    @params fuzzy: can this motif be fuzzy?
    """
    # create the directory structure
    if not os.path.exists('motifs'):
        os.mkdir('motifs')
    if not os.path.exists('motifs/subgraphs'):
        os.mkdir('motifs/subgraphs')
    if not os.path.exists('motifs/subgraphs/{}'.format(dataset)):
        os.mkdir('motifs/subgraphs/{}'.format(dataset))

    # read the frequent subgraphs for this dataset/request type
    subgraphs = IdentifyFrequentSubgraphs(dataset, request_type, True, fuzzy)
    # read all of the traces
    traces = ReadTraces(dataset, request_type, None)

    subgraphs_found = set()

    for trace in traces:
        # start statistics
        start_time = time.time()

        # reduced nodes to nodes is a funciton to go from the reduced node space to the original
        graph, reduced_nodes_to_nodes = ConvertCollapsedGraph2GraphTool(trace, fuzzy)
        motifs = []

        for motif_index, subgraph in enumerate(subgraphs):
            motif = ConvertSubGraph2GraphTool(subgraph)

            # use graph tool to find all motif occurrences
            vertex_maps = gt.subgraph_isomorphism(motif, graph, vertex_label=(motif.vp.label, graph.vp.label))

            # go through all of the found motif patterns
            for vertex_map in vertex_maps:
                nodes = []
                # add all of the nodes that belong to each vertex (collapsed nodes)
                for reduced_node in vertex_map:
                    for node in reduced_nodes_to_nodes[reduced_node]:
                        assert (not trace.nodes[node] in nodes)
                        nodes.append(trace.nodes[node])
                subgraphs_found.add(motif_index)
                motifs.append(Motif(trace, nodes, motif_index))

        # write the motifs to disk
        if fuzzy: output_filename = 'motifs/subgraphs/{}/{}-motifs-fuzzy-collapsed-complete.motifs'.format(dataset, trace.base_id)
        else: output_filename = 'motifs/subgraphs/{}/{}-motifs-collapsed-complete.motifs'.format(dataset, trace.base_id)

        WriteMotifs(output_filename, motifs)

        # print statistics
        print ('Mined traces for {} in {:0.2f} seconds.'.format(trace.base_id, time.time() - start_time))
