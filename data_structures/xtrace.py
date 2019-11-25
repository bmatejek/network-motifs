from network_motifs.data_structures.trace import Trace, TraceNode, TraceEdge



class XTrace(Trace):
    def __init__(self, nodes, edges, request_type, request, base_id):
        self.request = request

        Trace.__init__(self, nodes, edges, request_type, base_id)

        def Filename(self):
            return 'xtraces-json/{}.json'.format(base_id)



class XTraceNode(TraceNode):
    def __init__(self, id, parent_id, function_id, timestamp):
        TraceNode.__init__(self, id, parent_id, function_id, timestamp)

    def Name(self):
        return self.function_id



class XTraceEdge(TraceEdge):
    def __init__(self, source, destination, duration):
        TraceEdge.__init__(self, source, destination, duration)
