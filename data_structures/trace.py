class Trace(object):
    def __init__(self, nodes, edges, request_type, base_id):
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
        # this method needs to be overridden by inherited classes
        assert (False)

    def UniqueFunctions(self):
        functions = set()

        for node in self.nodes:
            functions.add(node.function_id)

        return functions

    def UniqueNames(self):
        names = set()

        for node in self.nodes:
            names.add(node.Name())

        return names

    def WriteToFile(self):
        # this method needs to be overridden by inherited classes
        assert (False)

    def KthNode(self, k):
        # ignore out of range nodes
        if k < 0: return None
        if k >= len(self.nodes): return None
        # return the nodes at this location
        return self.ordered_nodes[k]



class TraceNode(object):
    def __init__(self, id, function_id, timestamp):
        self.id = id
        self.function_id = function_id
        self.timestamp = timestamp

        # will be updated when creating Trace object
        self.children_nodes = []
        self.parent_nodes = []
        self.sequence = None
        self.index = -1

    def Name(self):
        # this needs to be overridden by inherited classes
        assert (False)



class TraceEdge(object):
    def __init__(self, source, destination, duration):
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

    def AddNode(self, node):
        """
        Add a node to the current sequence
        @param node: node to be added to the sequence. it's parent should be
        immediately before it in the list. Nodes can have only one parent to be
        in the sequence
        """
        assert (len(node.parent_nodes) == 1)
        assert (self.nodes[-1] == node.parent_nodes[0])
        self.nodes.append(node)





def GetUniqueFunctions(traces):
    functions = set()

    for trace in traces:
        functions = functions | trace.UniqueFunctions()

    return sorted(list(functions))



def GetUniqueNames(dataset):
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



def GetUniqueRequestTypes(traces):
    request_types = set()

    for trace in traces:
        request_types.add(trace.request_type)

    return sorted(list(request_types))
