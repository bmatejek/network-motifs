import os
import struct



import pandas as pd



from network_motifs.motifs.motif import ReadMotifs



class Trace(object):
    def __init__(self, dataset, nodes, edges, request_type, base_id):
        """
        Initialize a trace object given an input graph. The constructor also
        initializes attributes for the nodes and edges objects so needs to be
        called with populated nodes and edges. Also creates mappings from
        node_to_index and an list of nodes ordered by timestamp. For easier use,
        there are also attributes minimum_timestamp and maximum_timestamp.
        Sequences represent linear, one-to-one sequence occurrences in the graph.
        Motifs are added if the file can be read from disk.
        @params dataset: the name of the dataset corresponding to tracing method
        @param nodes: list of nodes corresponding to this trace
        @param edges: list of edges corresponding to this trace
        @param request_type: the request that started this execution trace
        @param base_id: a unique identifier for this trace
        """
        self.dataset = dataset
        self.nodes = nodes
        self.edges = edges
        self.request_type = request_type
        self.base_id = base_id
        self.node_to_index = {}

        # order the nodes by timestamp
        self.ordered_nodes = []

        # populate the helper dictionaries
        for iv, node in enumerate(nodes):
            self.node_to_index[node] = iv
            node.index = iv

        # need this separately since ordering of nodes can change
        for edge in self.edges:
            edge.destination.parent_nodes.append(edge.source)
            edge.source.children_nodes.append(edge.destination)

        # make sure that the first node is a root node
        assert (not len(self.nodes[0].parent_nodes))

        # create a new list of sequences for this trace
        self.sequences = []

        # the root starts a new sequence
        sequence = TraceNodeSequence(self.nodes[0], len(self.sequences))
        self.sequences.append(sequence)
        self.nodes[0].sequence = sequence

        # add the root node to the list of current nodes
        current_nodes = []
        current_nodes.append(self.nodes[0])
        # keep track of the nodes that are visited so we do not go over paths more than once
        visited_nodes = [False for iv in range(len(self.nodes))]

        while len(current_nodes):
            # remove the current node from the list
            current_node = current_nodes.pop(0)

            # if already visited do not add its kids
            if visited_nodes[current_node.index]: continue

            # if this node has only one parent and one (or no) child, it belongs to a sequence
            if len(current_node.parent_nodes) == 1 and len(current_node.children_nodes) < 2:
                # if the parent does not belong to a sequence, start a new sequence
                if current_node.parent_nodes[0].sequence == None:
                    sequence = TraceNodeSequence(current_node, len(self.sequences))
                    self.sequences.append(sequence)
                    current_node.sequence = sequence
                # else this node becomes part of its parent's sequence
                else:
                    sequence = current_node.parent_nodes[0].sequence
                    sequence.AddNode(current_node)
                    current_node.sequence = sequence

            # mark this node as visited and add its kids to the list of current nodes
            visited_nodes[current_node.index] = True

            for child_node in current_node.children_nodes:
                # do not revist the children if already seen (other path to them)
                if visited_nodes[child_node.index]: continue
                # add to the end of the list
                current_nodes.append(child_node)

        # order the nodes
        self.ordered_nodes = sorted(self.nodes, key=lambda x: (x.timestamp, x.index, x.function_id))

        # make sure that the first node is the start of the chain
        assert (len(self.ordered_nodes[0].parent_nodes) == 0)

        # get the total running time for this trace
        self.duration = self.ordered_nodes[-1].timestamp - self.ordered_nodes[0].timestamp
        assert (self.duration > 0)

        # get the extreme values for the timestamps
        self.minimum_timestamp = self.ordered_nodes[0].timestamp
        self.maximum_timestamp = self.ordered_nodes[-1].timestamp

        # update the timestamps so that the root node is at time 0
        for node in self.nodes:
            node.timestamp = node.timestamp - self.minimum_timestamp
            assert (node.timestamp >= 0)

        # update the extreme values in the new frame
        self.minimum_timestamp = self.ordered_nodes[0].timestamp
        self.maximum_timestamp = self.ordered_nodes[-1].timestamp

        # read the motifs if the file exists
        self.motifs = ReadMotifs(self.dataset, self, 'pruned')
        self.collapsed_motifs = ReadMotifs(self.dataset, self, 'collapsed-pruned')
        self.fuzzy_collapsed_motifs = ReadMotifs(self.dataset, self, 'fuzzy-collapsed-pruned')

        # add the references for each motif
        for motif in self.motifs:
            for node in motif.nodes:
                assert (node.motif == None)
                node.motif = motif
        for motif in self.collapsed_motifs:
            for node in motif.nodes:
                assert (node.collapsed_motif == None)
                node.collapsed_motif = motif
        for motif in self.fuzzy_collapsed_motifs:
            for node in motif.nodes:
                assert (node.fuzzy_collapsed_motif == None)
                node.fuzzy_collapsed_motif = motif


    def Filename(self):
        """
        Overriden method that returns the file location for this trace.
        """
        # this method needs to be overridden by inherited classes
        assert (False)

    def UniqueFunctions(self):
        """
        Returns the unique functions for all nodes in this trace.
        """
        functions = set()

        for node in self.nodes:
            functions.add(node.function_id)

        return functions

    def UniqueNames(self):
        """
        Returns the list of unique names for all nodes in this trace. Can differ
        from children traces since names can rely on variants/attributes.
        """
        names = set()

        for node in self.nodes:
            names.add(node.Name())

        return names

    def WriteToFile(self):
        """
        Overridden method that writes this trace to file.
        """
        # this method needs to be overridden by inherited classes
        assert (False)

    def KthNode(self, k):
        """
        @param k: the index of the node we want
        Returns the kth node in the ordered list of nodes
        """
        # ignore out of range nodes
        if k < 0: return None
        if k >= len(self.nodes): return None
        # return the nodes at this location
        return self.ordered_nodes[k]



class TraceNode(object):
    def __init__(self, id, function_id, timestamp):
        """
        Constructor for the TraceNode object that represents one node in the graph.
        The attributes children_nodes, parent_nodes, sequence, and index are
        populated when the node is sent to the Trace constructor.
        @param id: the id for this node (should be unique among entry/exit)
        @param function_id: what function corresponds to this node.
        @param timestamp: when did this node occur.
        """
        self.id = id
        self.function_id = function_id
        self.timestamp = timestamp

        # will be updated when creating Trace object
        self.children_nodes = []
        self.parent_nodes = []
        self.sequence = None
        # three different possible motif options
        self.motif = None
        self.collapsed_motif = None
        self.fuzzy_collapsed_motif = None
        self.index = -1

    def Name(self):
        """
        Overriden method that returns an identifier for this node.
        """
        # this needs to be overridden by inherited classes
        assert (False)



class TraceEdge(object):
    def __init__(self, source, destination, duration):
        """
        Constructor for the TraceEdge object that represents one edge in the graph.
        @param source: the source TraceNode object
        @param destination: the destination TraceNode object
        @param duration: the time duration for this edge (difference of timestamps)
        """
        self.source = source
        self.destination = destination
        self.duration = duration



class TraceNodeSequence(object):
    """
    TraceNodeSequence: a list of nodes in a trace that belong to a sequential
    path where every element in the path has at most one parent and one child
    except the first and last elements.
    """
    def __init__(self, root_node, index):
        """
        Construct a node sequence from this list of nodes.
        @param root_node: the first node in the sequence, others will be added
        @param index: the index in the parent trace (for graph coloring)
        """
        self.nodes = []
        self.nodes.append(root_node)
        self.index = index
        # initialize the duration to be 0, updated when adding nodes
        self.duration = 0
        self.minimum_timestamp = root_node.timestamp
        self.maximum_timestamp = root_node.timestamp

    def AddNode(self, node):
        """
        Add a node to the current sequence
        @param node: node to be added to the sequence. it's parent should be
        immediately before it in the list. Nodes can have only one parent to be
        in the sequence
        """
        assert (len(node.parent_nodes) == 1)
        assert (self.nodes[-1] == node.parent_nodes[0])
        assert (self.nodes[-1].timestamp <= node.timestamp)
        self.nodes.append(node)
        self.duration = self.nodes[-1].timestamp - self.nodes[0].timestamp
        self.maximum_timestamp = self.nodes[-1].timestamp

    def SequenceTuple(self):
        """
        Generate a tuple for the sequence so that sequences can be compared.
        Returns the sequence of nodes as a tuple.
        """
        sequence = ()
        for node in self.nodes:
            sequence = sequence + (node.Name(), )

        return sequence



def GetUniqueFunctions(traces):
    """
    Returns the unique set of functions for the input list of traces.
    """
    functions = set()

    for trace in traces:
        functions = functions | trace.UniqueFunctions()

    return sorted(list(functions))



def GetUniqueNames(dataset):
    """
    Returns a mapping from a unique name in the dataset to an id.
    @param dataset: the dataset for these unique names
    """
    mapping_filename = 'mappings/{}/name-to-index.txt'.format(dataset)

    with open(mapping_filename, 'r') as fd:
        names = fd.read().splitlines()

    # needed for quick motif discovery calculations
    name_to_index = {}
    index_to_name = {}

    for iv, name in enumerate(names):
        name_to_index[name] = iv
        index_to_name[iv] = name

    return name_to_index



def GetUniqueNodeSequences(dataset, fuzzy):
    """
    Returns a mapping from a unique sequence in the dataset to an id.
    @params dataset: the dataset for these unique names
    @params fuzzy: allow fuzzy sequences or not for this dataset
    """
    # read the input file from disk
    if fuzzy: input_filename = 'mappings/{}/fuzzy-node-sequence-to-index.txt'.format(dataset)
    else: input_filename = 'mappings/{}/hard-node-sequence-to-index.txt'.format(dataset)

    sequence_to_index = {}

    # read the sequence mapping file
    with open(input_filename, 'r') as fd:
        nsequences = int(fd.readline().strip())
        # go through all sequences
        for _ in range(nsequences):
            sequence_length = int(fd.readline().strip())
            sequence = ()
            # read in all the nodes in the sequence
            for _ in range(sequence_length):
                sequence = sequence + (fd.readline().strip(),)
            # create the mapping
            sequence_id = int(fd.readline().strip())
            sequence_to_index[sequence] = sequence_id

    return sequence_to_index



def ReadCollapsedSequences(trace, cache_filename):
    """
    Read the collapsed sequences from file if they exist.
    @params cache_filename: the file that conatains the cached data.
    """
    # get the dataset for this trace
    dataset = trace.dataset

    # first read the node mapping
    nnodes = len(trace.nodes)
    node_mapping = {}
    reduced_nodes_to_nodes = {}
    node_labels = []
    node_label_names = []
    edges = []

    with open(cache_filename, 'rb') as fd:
        # read the forward node mapping
        for iv in range(nnodes):
            mapped_value, = struct.unpack('q', fd.read(8))
            node_mapping[iv] = mapped_value

        # read the backwards mapping
        nreduced_nodes, = struct.unpack('q', fd.read(8))
        for iv in range(nreduced_nodes):
            reduced_nodes_to_nodes[iv] = []
            no_nodes_reduced, = struct.unpack('q', fd.read(8))
            for ip in range(no_nodes_reduced):
                node, = struct.unpack('q', fd.read(8))
                reduced_nodes_to_nodes[iv].append(node)

        for iv in range(nreduced_nodes):
            label, = struct.unpack('q', fd.read(8))
            node_labels.append(label)

        # maximum bytes depends on the dataset
        if dataset == 'openstack': max_bytes = 196
        elif dataset == 'xtrace': max_bytes = 64
        else: assert (False)

        # read the node label names
        for iv in range(nreduced_nodes):
            node_label_name_bytes, = struct.unpack('%ds' % max_bytes, fd.read(max_bytes))
            node_label_name = node_label_name_bytes.decode().strip('\0')
            node_label_names.append(node_label_name)

        # read the edges
        nedges, = struct.unpack('q', fd.read(8))
        for _ in range(nedges):
            source_index, destination_index, = struct.unpack('qq', fd.read(16))
            edges.append((source_index, destination_index))

    return node_mapping, reduced_nodes_to_nodes, node_labels, node_label_names, edges



def CollapseSequences(trace, fuzzy):
    """
    Collapse the sequences in the graph for faster motif discovery.
    @params trace: the trace to collapse the sequences for
    @params fuzzy: allow fuzzy sequences or not for this dataset
    """
    # get the dataset for this trace
    dataset = trace.dataset
    base_id = trace.base_id

    # use a cached version of this file if it exists
    if fuzzy: cache_filename = 'cache/{}/{}-fuzzy-collapsed.graph'.format(dataset, base_id)
    else: cache_filename = 'cache/{}/{}-collapsed.graph'.format(dataset, base_id)

    if os.path.exists(cache_filename):
        return ReadCollapsedSequences(trace, cache_filename)

    # create the mapping to from sequences to names
    sequence_to_index = GetUniqueNodeSequences(dataset, fuzzy)
    name_to_index = GetUniqueNames(dataset)
    nnames = len(name_to_index)

    # create a mapping to nodes to reduce the sequences
    node_mapping = {}
    reduced_nodes_to_nodes = {}

    for node in trace.nodes:
        if node.sequence == None:
            node_mapping[node.index] = node.index
        else:
            node_mapping[node.index] = len(trace.nodes) + node.sequence.index

    # create a mapping to a reduced set of nodes
    reduced_node_mapping = {}
    unique_nodes = sorted(pd.unique(list(node_mapping.values())))

    for iv, value in enumerate(unique_nodes):
        reduced_node_mapping[value] = iv
    # update the node mappings so no longer need reduced node mapping
    for key in node_mapping:
        node_mapping[key] = reduced_node_mapping[node_mapping[key]]

    # create the node labels and the node names
    nnodes = len(reduced_node_mapping)

    node_labels = [0 for _ in range(nnodes)]
    node_label_names = ['' for _ in range(nnodes)]

    for node in trace.nodes:
        new_node_index = node_mapping[node.index]

        # add this node to the reduced list for easier back movement
        if not new_node_index in reduced_nodes_to_nodes:
            reduced_nodes_to_nodes[new_node_index] = []
        reduced_nodes_to_nodes[new_node_index].append(node.index)

        sequence = node.sequence
        if sequence == None:
            node_label_names[new_node_index] = node.Name()
            node_labels[new_node_index] = name_to_index[node.Name()]
        else:
            # subtract the number of names so sequence indices start at 0
            node_label_names[new_node_index] = 'Sequence {}'.format(sequence_to_index[sequence.SequenceTuple()] - nnames)
            node_labels[new_node_index] = sequence_to_index[sequence.SequenceTuple()]

    # create a list of edges
    edges = []
    for edge in trace.edges:
        source_index = node_mapping[edge.source.index]
        destination_index = node_mapping[edge.destination.index]
        # don't include self loops caused by sequences
        if source_index == destination_index: continue
        edges.append((source_index, destination_index))

    # create an output directory if needed
    if not os.path.exists('cache'):
        os.mkdir('cache')
    if not os.path.exists('cache/{}'.format(dataset)):
        os.mkdir('cache/{}'.format(dataset))

    # save the relevant information to disk
    with open(cache_filename, 'wb') as fd:
        # write the forward mapping
        for node in trace.nodes:
            fd.write(struct.pack('q', node_mapping[node.index]))

        # write the reverse mapping
        nreduced_nodes = len(reduced_nodes_to_nodes)
        fd.write(struct.pack('q', nreduced_nodes))
        for iv in range(nreduced_nodes):
            no_nodes_reduced = len(reduced_nodes_to_nodes[iv])
            fd.write(struct.pack('q', no_nodes_reduced))
            for ip in range(no_nodes_reduced):
                fd.write(struct.pack('q', reduced_nodes_to_nodes[iv][ip]))

        # write the node labels
        for iv in range(nreduced_nodes):
            fd.write(struct.pack('q', node_labels[iv]))

        # maximum bytes depends on the dataset
        if dataset == 'openstack': max_bytes = 196
        elif dataset == 'xtrace': max_bytes = 64
        else: assert (False)

        # write the node label names
        for iv in range(nreduced_nodes):
            node_label_name_bytes = node_label_names[iv].encode()
            assert (len(node_label_name_bytes) <= max_bytes)
            fd.write(struct.pack('%ds' % max_bytes, node_label_name_bytes))

        # write all of the
        nedges = len(edges)
        fd.write(struct.pack('q', nedges))
        for (source_index, destination_index) in edges:
            fd.write(struct.pack('qq', source_index, destination_index))

    # return the nodes, edges, and various mappings
    return node_mapping, reduced_nodes_to_nodes, node_labels, node_label_names, edges
