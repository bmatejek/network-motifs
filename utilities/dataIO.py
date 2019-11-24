import json


import pandas as pd


from network_motifs.data_structures.open_stack import OpenStackTrace, OpenStackNode, OpenStackEdge



def VerifyKeys(data, keys):
    # make sure every trace has these keys
    for key, value in data.items():
        assert (key in keys)
        keys.remove(key)

    assert (not len(keys))



def ReadOpenStackTrainingFilenames():
    training_list_filename = 'openstack-json/training-open-stack-traces.txt'
    with open(training_list_filename, 'r') as fd:
        return fd.read().splitlines()



def ReadOpenStackTestingFilenames():
    testing_list_filename = 'openstack-json/testing-open-stack-traces.txt'
    with open(testing_list_filename, 'r') as fd:
        return fd.read().splitlines()



def ReadOpenStackJSONTrace(json_filename):
    # open the JSON file
    with open(json_filename, 'r') as fd:
        data = json.load(fd)

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
    json_nodes = graph['nodes']
    json_edges = graph['edges']

    # create new lists for the internal format
    nodes = []
    edges = []

    # cannot handle node holes at the moment
    assert (not len(graph['node_holes']))

    # only care about directed graphs
    assert (graph['edge_property'] == 'directed')

    # create a new graph structure for each trace
    for json_node in json_nodes:
        # the unique identifier for this node
        trace_id = json_node['span']['trace_id']
        # the parent that led to this node
        parent_id = json_node['span']['parent_id']
        # the actual function that is envoked
        tracepoint_id = json_node['span']['tracepoint_id']
        # the time of this particular action
        timestamp = pd.to_datetime(json_node['span']['timestamp'])
        # the action associated with this node (entry, exit, or annotation)
        variant = json_node['span']['variant']

        nodes.append(OpenStackNode(trace_id, parent_id, tracepoint_id, timestamp, variant))

    for json_edge in json_edges:
        # get the source and destination nodes
        source = json_edge[0]
        destination = json_edge[1]

        # get the time for this edge
        seconds = json_edge[2]['duration']['secs']
        nanoseconds = json_edge[2]['duration']['nanos']
        duration = seconds * 10 ** 9 + nanoseconds

        # make sure that the edge takes a non trivial amount of time
        assert (not duration == 1)

        # the action associated with this node
        variant = json_edge[2]['variant']

        edges.append(OpenStackEdge(nodes, source, destination, duration, variant))

    # create the new json trace object
    return OpenStackTrace(nodes, edges, request_type, base_id)



def ReadXTraceJSONTrace(json_filename):
    # open the JSON file
    with open(json_filename, 'r') as fd:
        data = json.load(fd)

    # verify the json file follows the expected format
    VerifyKeys(data, ['id', 'reports'])

    # read the base id for this trace
    base_id = data['id']
    assert (base_id in json_filename)

    # read in the data from the reports
    reports = data['reports']
    nnodes = len(reports)

    # go through each function in the report
    for report in reports:
        # get the event and parent id
        event_id = report['EventID']
        parent_id = report['ParentEventID']

        # get the time of this action
        timestamp = pd.to_datetime(report['Timestamp'])

        if not 'Source' in report:
            print (report)
        else:
            print (report['Source'])
            print (parent_id)

        label = report['Label']



    exit()
