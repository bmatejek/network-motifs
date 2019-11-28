import heapq



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

        # make sure that the first node is the start of the chain
        assert (len(self.nodes[0].parent_nodes) == 0)

        # run Dijkstra's algorithm to get the rank of each node
        nnodes = len(self.nodes)
        visited = [False for _ in range(nnodes)]
        popped = [False for _ in range(nnodes)]
        ranks = [2 * nnodes for _ in range(nnodes)]
        heap = []

        # the first node has rank 0 and is visited
        ranks[0] = 0
        visited[0] = True
        # the rank of the node, the dummy counter variable for every push
        # and the index for the node
        heap.append((ranks[0], 0, 0))
        # dummy counter variable
        counter = 1

        while (len(heap)):
            # pop the element closest to the root
            rank, _, index = heapq.heappop(heap)
            # skip if already seen
            if popped[index]: continue

            # so not to revisit this node
            popped[index] = True

            for neighbor_node in (self.nodes[index].parent_nodes + self.nodes[index].children_nodes):
                if (not visited[neighbor_node.index]):
                    ranks[neighbor_node.index] = rank + 1
                    visited[neighbor_node.index] = True
                    heapq.heappush(heap, (ranks[neighbor_node.index], counter, neighbor_node.index))
                    counter += 1
                elif rank + 1 < ranks[neighbor_node.index]:
                    ranks[neighbor_node.index] = rank + 1
                    heapq.heappush(heap, (ranks[neighbor_node.index], counter, neighbor_node.index))
                    counter += 1

        # update the attributes for this node
        for node in self.nodes:
            node.rank = ranks[node.index]
            assert (visited[node.index] == True)
            assert (popped[node.index] == True)

        # get a list of the nodes ordered by timestamp
        self.ordered_nodes = sorted(self.nodes, key=lambda x: (x.timestamp, x.rank, x.function_id))



    def Filename(self):
        # this method needs to be overridden by inherited classes
        assert (False)

    def UniqueFunctions(self):
        functions = set()

        for node in self.nodes:
            functions.add(node.function_id)

        return functions

    def WriteToFile(self):
        # this method needs to be overridden by inherited classes
        assert (False)



class TraceNode(object):
    def __init__(self, id, function_id, timestamp):
        self.id = id
        self.function_id = function_id
        self.timestamp = timestamp

        # will be updated when creating Trace object
        self.children_nodes = []
        self.parent_nodes = []
        self.index = -1
        self.rank = -1

    def Name(self):
        # this needs to be overridden by inherited classes
        assert (False)

    def ParentNode(self):
        # return the first parent node
        if not len(self.parent_nodes): return None
        else: return self.parent_nodes[0]





class TraceEdge(object):
    def __init__(self, source, destination, duration):
        self.source = source
        self.destination = destination
        self.duration = duration
