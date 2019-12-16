import os
import time
import struct



import graph_tool.all as gt



from network_motifs.transforms.convert import ConvertTrace2GraphTool, ConvertSubGraph2GraphTool
from network_motifs.motifs.motif import Motif, SubGraph
from network_motifs.utilities.dataIO import ReadTraces



def IdentifyFrequentSubgraphs(dataset, request_type):
    """
    Populate an array of frequent subgraphs found using the GASTON algorithm.
    @params dataset: the dataset to mine for frequent sub graphs
    @params request_type: the request type for this set of traces
    """
    # create a list of subgraphs to mine for
    subgraphs = []

    # read the subgraphs generated from GASTON
    subgraph_filename = 'motifs/patterns/{}/{}-gaston-patterns.txt'.format(dataset, request_type)
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
    subgraphs = IdentifyFrequentSubgraphs(dataset, request_type)

    # read all of the traces and mine the graph
    traces = ReadTraces(dataset, request_type)

    for trace in traces:
        graph = ConvertTrace2GraphTool(dataset, trace)
        motifs = []

        for subgraph in subgraphs:
            motif = ConvertSubGraph2GraphTool(subgraph)

            # use graph tool to find all motif occurrences
            vertex_maps = gt.subgraph_isomorphism(motif, graph, vertex_label=(motif.vp.label, graph.vp.label))

            # go through all of the found motif patterns
            for vertex_map in vertex_maps:
                nodes = []
                for node in vertex_map:
                    nodes.append(trace.nodes[node])
                motifs.append(Motif(trace, nodes))

        # save the motif to disk
        motif_filename = 'motifs/subgraphs/{}/{}.motifs'.format(dataset, trace.base_id)
        with open(motif_filename, 'wb') as fd:
            fd.write(struct.pack('q', len(motifs)))
            for motif in motifs:
                nnodes = len(motif.nodes)
                fd.write(struct.pack('q', nnodes))
                for node in motif.nodes:
                    fd.write(struct.pack('q', node.index))

    # print statistics
    print ('Mined traces for {} request {} in {:0.2f} seconds.'.format(dataset, request_type, time.time() - start_time))
