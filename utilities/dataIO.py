import json
import datetime


import pandas as pd


from network_motifs.data_structures.json_graph import JSONNode, JSONEdge



def ReadEmreJSONTrace(json_filename):
    # open the JSON file
    with open(json_filename, 'r') as fd:
        data = json.load(fd)

    graph = data['g']

    # read the nodes and edges from the graph
    nodes = graph['nodes']
    edges = graph['edges']

    json_nodes = []
    json_edges = []

    # go through each node
    for node in nodes:
        # equivalent to the node index
        trace_id = node['span']['trace_id']
        # unique to each function
        tracepoint_id = node['span']['tracepoint_id']
        # time of function entry or exit
        timestamp = pd.to_datetime(node['span']['timestamp'])
        # what type of node is this
        variance = node['span']['variant']

        json_nodes.append(JSONNode(trace_id, tracepoint_id, timestamp, variance))

    for edge in edges:
        # source node
        source = nodes[edge[0]]
        destination = nodes[edge[1]]
        seconds = int(edge[2]['duration']['secs'])
        nanoseconds = int(edge[2]['duration']['nanos'])
        duration = seconds * 10**9 + nanoseconds
        variance = edge[2]['variant']

        # there are fake edges with one nanosecond duration
        if duration == 1: continue

        json_edges.append(JSONEdge(source, destination, timestamp, variance))

    return json_nodes, json_edges