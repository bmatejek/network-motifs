import os
import json
import glob
import time



import pandas as pd
import graph_tool.all as gt



from network_motifs.data_structures.open_stack import OpenStackTrace, OpenStackNode, OpenStackEdge
from network_motifs.data_structures.trace import GetUniqueNames, CollapseSequences
from network_motifs.data_structures.xtrace import XTrace, XTraceNode, XTraceEdge
from network_motifs.graphs.visualize import VisualizeCollapsedGraph
from network_motifs.utilities.dataIO import ReadFilenames, ReadTraces
from network_motifs.utilities.constants import request_types_per_dataset



def VerifyKeys(data, keys):
    """
    Verify that the data conatins all of the keys.
    @params data: dictionary for verifcation
    @params keys: keys to verify are in the dictionary
    """
    # make sure every trace has these keys
    for key, value in data.items():
        assert (key in keys)
        keys.remove(key)

    assert (not len(keys))



def ReadJSONTrace(dataset, json_filename):
    """
    Read the trace from the original JSON filename
    @params dataset: the dataset name for the traces
    @params json_filename: the JSON filename that contains the trace
    """
    # generic read file for easier access to OpenStack and XTrace reads
    if dataset == 'openstack': return ReadOpenStackJSONTrace(json_filename)
    elif dataset == 'xtrace': return ReadXTraceJSONTrace(json_filename)
    else: assert (False)



def ReadOpenStackJSONTrace(json_filename):
    """
    Read the OpenStack JSON trace into an OpenStackTrace data structure
    and save to file.
    @params json_filename: the JSON filename that contains the trace.
    """
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
    trace = OpenStackTrace('openstack', nodes, edges, request_type, base_id)

    trace.WriteToFile()



def ReadXTraceJSONTrace(json_filename):
    """
    Read the XTrace JSON trace into an XTrace data structure
    and save to file.
    @params json_filename: the JSON filename that contains the trace.
    """
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
        # skip edges where the parent id does not exist
        if not edge[0] in id_to_node: continue

        # get the parent and child node
        parent_node = id_to_node[edge[0]]
        child_node = id_to_node[edge[1]]

        duration = child_node.timestamp - parent_node.timestamp
        assert (duration >= 0)

        edges.append(XTraceEdge(parent_node, child_node, duration))

    # make sure there is only one tag per trace
    assert (len(tags) == 1)
    request = list(tags)[0]
    request_type = request.split(' ')[0].strip('-')

    # create the new trace object and write to file
    trace = XTrace('xtrace', nodes, edges, request_type, request, base_id)

    trace.WriteToFile()



def ConvertJSON2Trace(dataset):
    """
    Convert all of the JSON traces in the dataset into the .trace file type
    @params dataset: the type of trace to convert
    """
    # make sure the output directory exists
    if not os.path.exists('traces'):
        os.mkdir('traces')
    if not os.path.exists('traces/{}'.format(dataset)):
        os.mkdir('traces/{}'.format(dataset))

    # start statistics
    start_time = time.time()

    filenames = glob.glob('jsons/{}/*json'.format(dataset))

    for filename in filenames:
        ReadJSONTrace(dataset, filename)

    print ('Converted JSON files for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))



def ConvertTrace2GastonGraph(dataset, request_type, traces):
    """
    Convert the trace into a gaston graph where nodes stack on each other.
    @params dataset: the dataset that the traces come from
    @params request_type: the request type for this particular set of traces
    @params traces: all of the traces for this dataset request type combo
    """
    # read the mapping from nodes to indices
    name_to_index = GetUniqueNames(dataset)

    # create the gaston file
    gaston_filename = 'graphs/{}/{}-gaston.txt'.format(dataset, request_type)
    with open(gaston_filename, 'w') as fd:
        # go through each trace and add the node and edges to the file
        for trace_index, trace in enumerate(traces):
            fd.write('t # {}\n'.format(trace_index))

            # go through each node in this trace
            for node in trace.nodes:
                # check to make sure each node is unique
                name_index = name_to_index[node.Name()]

                #fd.write('v {:07d} {:04d}\n'.format(node.index, name_index))
                fd.write('v {:07d} {:04d}\n'.format(node.index, name_index))

            # go through each edge in the trace
            for edge in trace.edges:
                # get the source and destination for this node
                source_index = edge.source.index
                destination_index = edge.destination.index

                fd.write('e {:07d} {:07d} 0\n'.format(source_index, destination_index))



def ConvertTrace2Graph(dataset):
    """
    Convert the traces for this dataset into formats for both GraMi and Gaston
    @params dataset: the type of trace to convert into motif discovery formats
    """
    # start statistics
    start_time = time.time()

    # make sure the output directory exists
    if not os.path.exists('graphs'):
        os.mkdir('graphs')
    if not os.path.exists('graphs/{}'.format(dataset)):
        os.mkdir('graphs/{}'.format(dataset))

    # get all of the request types for this dataset
    for request_type in request_types_per_dataset[dataset]:
        # read all the traces from this dataset
        traces = ReadTraces(dataset, request_type, None)

        ConvertTrace2GastonGraph(dataset, request_type, traces)

    print ('Converted trace files to graph for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))



def ConvertTrace2GraphTool(dataset, trace):
    """
    Convert the given trace into an object that can be used for graph tool functions.
    @params trace: the trace to convert into a graph tool object
    """
    graph = gt.Graph(directed=True)

    name_to_index = GetUniqueNames(dataset)

    # create a new property for the vertices
    labels = graph.new_vertex_property('int')

    for node in trace.nodes:
        vertex = graph.add_vertex()
        labels[vertex] = name_to_index[node.Name()]

    # add all of the edges into the graph
    for edge in trace.edges:
        source_index = edge.source.index
        destination_index = edge.destination.index
        graph.add_edge(source_index, destination_index)

    graph.vertex_properties['label'] = labels

    return graph



def ConvertSubGraph2GraphTool(subgraph):
    """
    Convert the SubGraph from frequent subgraph discovery algorithm into a graph tool object.
    @params subgraph: the subgraph to convert into a graph tool object
    """
    graph = gt.Graph(directed=True)

    # get the attributes for this subgraph
    vertices = subgraph.vertices
    edges = subgraph.edges

    # create a new property for the vertices
    labels = graph.new_vertex_property('int')

    for (_, label) in vertices:
        vertex = graph.add_vertex()
        labels[vertex] = label

    # add all of the edges into the graph
    for (source_index, destination_index) in edges:
        graph.add_edge(source_index, destination_index)

    graph.vertex_properties['label'] = labels

    return graph



def ConvertCollapsedGraphs2GastonGraph(dataset, fuzzy):
    """
    Collapse all of the graphs for this dataset, save a dot file for visualization,
    and produce a gaston file for motif discovery.
    @params dataset: the dataset to read the traces and collapse long sequences
    @params fuzzy: do we allow fuzzy motifs or not
    """
    # start statistics
    start_time = time.time()

    # go through all of the different request types
    request_types = request_types_per_dataset[dataset]
    for request_type in request_types:
        # create the gaston file for motif discovery
        if fuzzy: gaston_filename = 'graphs/{}/{}-fuzzy-collapsed-gaston.txt'.format(dataset, request_type)
        else: gaston_filename = 'graphs/{}/{}-collapsed-gaston.txt'.format(dataset, request_type)

        with open(gaston_filename, 'w') as fd:
            # go through each trace and add the nodes and edges to the file
            traces = ReadTraces(dataset, request_type, None)

            for trace_index, trace in enumerate(traces):
                # collapse all of the sequences
                node_labels, node_label_names, edges = CollapseSequences(trace, fuzzy)
                fd.write('t # {}\n'.format(trace_index))

                # add all of the nodes
                for iv, label in enumerate(node_labels):
                    fd.write('v {:07d} {:04d}\n'.format(iv, label))

                # add all of the edges
                for (source_index, destination_index) in edges:
                    fd.write('e {:07d} {:07d} 0\n'.format(source_index, destination_index))

                # visualize the results
                VisualizeCollapsedGraph(trace, node_label_names, edges, fuzzy)

    # print statistics
    print ('Converted collapsed graphs for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))
