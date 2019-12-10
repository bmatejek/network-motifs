import glob
import struct



from network_motifs.data_structures.open_stack import OpenStackTrace, OpenStackNode, OpenStackEdge
from network_motifs.data_structures.xtrace import XTrace, XTraceNode, XTraceEdge
from network_motifs.motifs.motif import Motif, Motifs



def ReadTrainingFilenames(dataset, request_type):
    training_list_filename = 'traces/{}/{}-training-traces.txt'.format(dataset, request_type)
    with open(training_list_filename, 'r') as fd:
        return fd.read().splitlines()



def ReadValidationFilenames(dataset, request_type):
    validation_list_filename = 'traces/{}/{}-validation-traces.txt'.format(dataset, request_type)
    with open(validation_list_filename, 'r') as fd:
        return fd.read().splitlines()



def ReadTrainValFilenames(dataset, request_type):
    return ReadTrainingFilenames(dataset, request_type) + ReadValidationFilenames(dataset, request_type)



def ReadTestingFilenames(dataset, request_type):
    testing_list_filename = 'traces/{}/{}-testing-traces.txt'.format(dataset, request_type)
    with open(testing_list_filename, 'r') as fd:
        return fd.read().splitlines()



def ReadFilenames(dataset, request_type=None):
    if request_type == None:
        return glob.glob('traces/{}/*trace'.format(dataset))
    else:
        return ReadTrainValFilenames(dataset, request_type) + ReadTestingFilenames(dataset, request_type)



def ReadTrace(dataset, trace_filename):
    if dataset == 'openstack': return ReadOpenStackTrace(trace_filename)
    elif dataset == 'xtrace': return ReadXTrace(trace_filename)
    else: assert (False)



def ReadOpenStackTrace(trace_filename):
    # maximum size for strings
    max_bytes = 48
    max_function_bytes = 196

    # open the file
    with open(trace_filename, 'rb') as fd:
        # create the list of nodes and edges
        nodes = []
        edges = []

        # read the request type for this trace
        request_type_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
        request_type = request_type_bytes.decode().strip('\0')
        # read the base id for this trace
        base_id_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
        base_id = base_id_bytes.decode().strip('\0')
        # read the nodes and edges
        nnodes, nedges, = struct.unpack('ii', fd.read(8))
        # read all of the nodes
        for iv in range(nnodes):
            node_id_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
            node_id = node_id_bytes.decode().strip('\0')
            # read the function id for this node
            function_id_bytes, = struct.unpack('%ds' % max_function_bytes, fd.read(max_function_bytes))
            function_id = function_id_bytes.decode().strip('\0')
            # read the timestamp
            timestamp, = struct.unpack('q', fd.read(8))
            # read the variant
            variant_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
            variant = variant_bytes.decode().strip('\0')

            # create this node after reading all attributes
            node = OpenStackNode(node_id, function_id, timestamp, variant)
            nodes.append(node)

        for ie in range(nedges):
            # get the source and destination indices
            source_index, destination_index, = struct.unpack('ii', fd.read(8))
            # read the duration of the edge
            duration, = struct.unpack('q', fd.read(8))
            variant_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
            # read the variant
            variant = variant_bytes.decode().strip('\0')

            # create this edge after reading all attributes
            edge = OpenStackEdge(nodes[source_index], nodes[destination_index], duration, variant)
            edges.append(edge)

        # create new trace object and return
        trace = OpenStackTrace(nodes, edges, request_type, base_id)

        return trace



def ReadXTrace(trace_filename):
    # maximum size for strings
    max_bytes = 32
    max_function_bytes = 64

    # open the file
    with open(trace_filename, 'rb') as fd:
        # create the list of nodes and edges
        nodes = []
        edges = []

        # read the request type for this trace
        request_type_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
        request_type = request_type_bytes.decode().strip('\0')
        # read the request  for this trace
        request_bytes, = struct.unpack('%ds' % max_function_bytes, fd.read(max_function_bytes))
        request = request_bytes.decode().strip('\0')
        # read the base id for this trace
        base_id_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
        base_id = base_id_bytes.decode().strip('\0')
        # read the nodes and edges
        nnodes, nedges, = struct.unpack('ii', fd.read(8))
        # read all of the nodes
        for iv in range(nnodes):
            node_id_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
            node_id = node_id_bytes.decode().strip('\0')
            # read the function id for this node
            function_id_bytes, = struct.unpack('%ds' % max_function_bytes, fd.read(max_function_bytes))
            function_id = function_id_bytes.decode().strip('\0')
            # read the timestamp
            timestamp, = struct.unpack('q', fd.read(8))

            # create this node after reading all attributes
            node = XTraceNode(node_id, function_id, timestamp)
            nodes.append(node)

        for ie in range(nedges):
            # get the source and destination indices
            source_index, destination_index, = struct.unpack('ii', fd.read(8))
            # read the duration of the edge
            duration, = struct.unpack('q', fd.read(8))

            # create this edge after reading all attributes
            edge = XTraceEdge(nodes[source_index], nodes[destination_index], duration)
            edges.append(edge)

        # create new trace object and return
        trace = XTrace(nodes, edges, request_type, request, base_id)

        return trace



def ReadMotifs(dataset, trace, pruned):
    # motif saved location
    if pruned: motif_filename = 'motifs/{}/{}-pruned.motifs'.format(dataset, trace.base_id)
    else: motif_filename = 'motifs/{}/{}-queried.motifs'.format(dataset, trace.base_id)

    with open(motif_filename, 'rb') as fd:
        nmotifs, = struct.unpack('i', fd.read(4))
        motifs = []

        # read all of the motifs from file
        for iv in range(nmotifs):
            motif_size, = struct.unpack('i', fd.read(4))
            # get the motif in question
            motif = ()
            for im in range(motif_size):
                element, = struct.unpack('i', fd.read(4))
                motif = motif + (element,)
            start_index, end_index, duration, = struct.unpack('iiq', fd.read(16))

            motifs.append(Motif(motif, start_index, end_index, duration))

        # create new motif object which sorts by end index
        return Motifs(dataset, trace, motifs)
