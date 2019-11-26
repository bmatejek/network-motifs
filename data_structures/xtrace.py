import struct



from network_motifs.data_structures.trace import Trace, TraceNode, TraceEdge



class XTrace(Trace):
    def __init__(self, nodes, edges, request_type, request, base_id):
        self.request = request

        Trace.__init__(self, nodes, edges, request_type, base_id)

    def Filename(self):
        return 'traces/xtrace/{}.trace'.format(self.base_id)

    def WriteToFile(self):
        # maximum size for strings
        max_bytes = 32
        max_function_bytes = 64

        with open(self.Filename(), 'wb') as fd:
            # write the request type
            request_type_bytes = self.request_type.encode()
            assert (len(request_type_bytes) <= max_bytes)
            fd.write(struct.pack('%ds' % max_bytes, request_type_bytes))
            # write the request
            request_bytes = self.request.encode()
            assert (len(request_bytes) <= max_function_bytes)
            fd.write(struct.pack('%ds' % max_function_bytes, request_bytes))
            # write the base id
            base_id_bytes = self.base_id.encode()
            assert (len(base_id_bytes) <= max_bytes)
            fd.write(struct.pack('%ds' % max_bytes, base_id_bytes))
            # write the number of nodes and edges
            nnodes = len(self.nodes)
            nedges = len(self.edges)
            fd.write(struct.pack('ii', nnodes, nedges))
            # write all of the nodes
            for node in self.nodes:
                node_id_bytes = node.id.encode()
                assert (len(node_id_bytes) <= max_bytes)
                fd.write(struct.pack('%ds' % max_bytes, node_id_bytes))
                # write the function id
                function_id_bytes = node.function_id.encode()
                assert (len(function_id_bytes) <= max_function_bytes)
                fd.write(struct.pack('%ds' % max_function_bytes, function_id_bytes))
                # write the timestamp
                fd.write(struct.pack('q', node.timestamp))

            # write all of the edges
            for edge in self.edges:
                # get the source and destination as indices
                source_index = self.node_to_index[edge.source]
                destination_index = self.node_to_index[edge.destination]
                fd.write(struct.pack('ii', source_index, destination_index))
                # write the duration of the edge
                duration = edge.duration
                fd.write(struct.pack('q', duration))



class XTraceNode(TraceNode):
    def __init__(self, id, function_id, timestamp):
        TraceNode.__init__(self, id, function_id, timestamp)

    def Name(self):
        return self.function_id



class XTraceEdge(TraceEdge):
    def __init__(self, source, destination, duration):
        TraceEdge.__init__(self, source, destination, duration)
