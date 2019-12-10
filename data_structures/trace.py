class Trace(object):
    def __init__(self, nodes, edges, request_type, base_id):
        """
        Initialize a trace object given an input graph. The constructor also
        initializes attributes for the nodes and edges objects so needs to be
        called with populated nodes and edges. Also creates mappings from
        node_to_index and an list of nodes ordered by timestamp. For easier use,
        there are also attributes minimum_timestamp and maximum_timestamp.
        Sequences represent linear, one-to-one sequence occurrences in the graph.
        @param nodes: list of nodes corresponding to this trace
        @param edges: list of edges corresponding to this trace
        @param request_type: the request that started this execution trace
        @param base_id: a unique identifier for this trace
        """
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
    Returns names, name_to_index, and index_to_name, corresponding to
    the unique names of functions in this dataset, a mapping from the name to
    an index, and the mapping from the index to the name.
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

    return names, name_to_index, index_to_name
