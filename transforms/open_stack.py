import json


import pandas as pd


from network_motifs.data_structures.open_stack import JSONTrace, JSONNode, JSONEdge



def VerifyKeys(data, keys):
    # make sure every trace has these keys
    for key, value in data.items():
        assert (key in keys)
        keys.remove(key)

    assert (not len(keys))



def ReadOpenStackJSONTrace(json_filename):
    # open the JSON file
    with open(json_filename, 'r') as fd:
        data = json.load(fd)
    #print (json_filename)
    # verify the json file follows the expected format
    VerifyKeys(data, ['g', 'base_id', 'start_node', 'end_node', 'request_type'])

    # read the entire graph structure
    graph = data['g']
    # verify the json file has the expected graph format
    VerifyKeys(graph, ['nodes', 'node_holes', 'edge_property', 'edges'])

    # read the base id for this trace
    base_id = data['base_id']
    assert (base_id in json_filename)

    # read the start and end nodes for this trace
    start_node = data['start_node']
    end_node = data['end_node']

    # read the request type for this trace
    request_type = data['request_type']

    # read all nodes and edges from the graph
    nodes = graph['nodes']
    edges = graph['edges']

    # create new lists for the internal format
    json_nodes = []
    json_edges = []

    # cannot handle node holes at the moment
    assert (not len(graph['node_holes']))

    # only care about directed graphs
    assert (graph['edge_property'] == 'directed')

    # create a new graph structure for each trace
    for node in nodes:
        # the unique identifier for this node
        trace_id = node['span']['trace_id']
        # the parent that led to this node
        parent_id = node['span']['parent_id']
        # the actual function that is envoked
        tracepoint_id = node['span']['tracepoint_id']
        # the time of this particular action
        timestamp = pd.to_datetime(node['span']['timestamp'])
        # the action associated with this node (entry, exit, or annotation)
        variant = node['span']['variant']

        json_nodes.append(JSONNode(trace_id, parent_id, tracepoint_id, timestamp, variant))

    for edge in edges:
        # get the source and destination nodes
        source = edge[0]
        destination = edge[1]

        # get the time for this edge
        seconds = edge[2]['duration']['secs']
        nanoseconds = edge[2]['duration']['nanos']
        duration = seconds * 10 ** 9 + nanoseconds

        # make sure that the edge takes a non trivial amount of time
        assert (not duration == 1)

        # the action associated with this node
        variant = edge[2]['variant']

        json_edges.append(JSONEdge(source, destination, duration, variant))

    # create the new json trace object
    return JSONTrace(json_nodes, json_edges, request_type)
