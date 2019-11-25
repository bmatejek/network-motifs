from network_motifs.data_structures.trace import Trace, TraceNode, TraceEdge



class OpenStackTrace(Trace):
    def __init__(self, nodes, edges, request_type, base_id):
        Trace.__init__(self, nodes, edges, request_type, base_id)

    def Filename(self):
        return 'openstack-json/{}.json'.format(base_id)



class OpenStackNode(TraceNode):
    def __init__(self, id, parent_id, function_id, timestamp, variant):
        self.variant = variant

        TraceNode.__init__(self, id, parent_id, function_id, timestamp)

    def Name(self):
        return '{} {}'.format(self.function_id, self.variant)



class OpenStackEdge(TraceEdge):
    def __init__(self, source, destination, duration, variant):
        self.variant = variant

        TraceEdge.__init__(self, source, destination, duration)
