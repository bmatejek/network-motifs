import json
import glob
import time



import pandas as pd



from network_motifs.data_structures.open_stack import OpenStackTrace, OpenStackNode, OpenStackEdge
from network_motifs.data_structures.xtrace import XTrace, XTraceNode, XTraceEdge



def VerifyKeys(data, keys):
    # make sure every trace has these keys
    for key, value in data.items():
        assert (key in keys)
        keys.remove(key)

    assert (not len(keys))



def ReadJSONTrace(dataset, json_filename):
    # generic read file for easier access to OpenStack and XTrace reads
    if dataset == 'openstack': return ReadOpenStackJSONTrace(json_filename)
    elif dataset == 'xtrace': return ReadXTraceJSONTrace(json_filename)
    else: assert (False)



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
        # the actual function that is envoked
        tracepoint_id = json_node['span']['tracepoint_id']
        # the time of this particular action
        timestamp = pd.to_datetime(json_node['span']['timestamp']).value
        # the action associated with this node (entry, exit, or annotation)
        variant = json_node['span']['variant']

        nodes.append(OpenStackNode(trace_id, tracepoint_id, timestamp, variant))

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

        edges.append(OpenStackEdge(nodes[source], nodes[destination], duration, variant))

    # create the new trace object and write to file
    trace = OpenStackTrace(nodes, edges, request_type, base_id)

    trace.WriteToFile()



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

    # keep track of all of the tags in this stack
    tags = set()

    # everything should have a source accept for a couple labels
    sourceless_labels = ['Executing command', 'netread']

    nodes = []                          # list of XTraceNodes
    edge_list = []                      # directed edges in ids
    id_to_node = {}                     # go from id to node

    # go through each function in the report
    for report in reports:
        # get the event and parent id
        event_id = report['EventID']
        parent_ids = report['ParentEventID']
        # remove the buffer variable for process starts
        if '0' in parent_ids: parent_ids.remove('0')

        # get the tag for this entry in the report
        if 'Tag' in report and not report['Tag'][0] == 'FsShell':
            assert (len(report['Tag']) == 1)
            tags.add(report['Tag'][0])

        # get the source or label for this node in the report
        if 'Source' in report:
            label = report['Label']
            assert (not label in sourceless_labels)
            source = report['Source']
        else:
            label = report['Label']
            assert (label in sourceless_labels)
            source = report['Label']

        # get the timestamp for this event
        timestamp = int(report['Timestamp'])

        # create the node and save a reference to it
        node = XTraceNode(event_id, source, timestamp)
        assert (not event_id in id_to_node)
        id_to_node[event_id] = node

        nodes.append(node)

        # add all of the relevant edges
        for parent_id in parent_ids:
            edge_list.append((parent_id, event_id))

    # convert the edge list into TraceEdges to construct a Trace object
    edges = []
    for edge in edge_list:
        parent_node = id_to_node[edge[0]]
        child_node = id_to_node[edge[1]]

        duration = child_node.timestamp - parent_node.timestamp

        edges.append(XTraceEdge(parent_node, child_node, duration))

    # make sure there is only one tag per trace
    assert (len(tags) == 1)
    request = list(tags)[0]
    request_type = request.split(' ')[0].strip('-')

    # create the new trace object and write to file
    trace = XTrace(nodes, edges, request_type, request, base_id)

    trace.WriteToFile()



def ConvertJSON2Trace(dataset):
    # start statistics
    start_time = time.time()

    filenames = glob.glob('jsons/{}/*json'.format(dataset))

    for filename in filenames:
        ReadJSONTrace(dataset, filename)

    print ('Converted JSON files for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))
