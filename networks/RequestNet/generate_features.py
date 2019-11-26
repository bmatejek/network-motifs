import glob



def GenerateFeatures(dataset, trace):
    # create an ordering of nodes from the timestamps
    node_with_timestamps = []

    for node in trace.nodes:
        node_with_timestamps.append((node.timestamp, node.Name()))

    node_with_timestamps.sort()

    # write the ordered sequence to disk
    output_filename = 'request-net/{}-features/{}.features'.format(dataset, trace.base_id)
    with open(output_filename, 'w') as fd:
        # write the request type
        fd.write('{}\n'.format(trace.request_type))
        for node in node_with_timestamps:
            fd.write('{}\n'.format(node[1]))



def FeatureWords(dataset):
    feature_filenames = glob.glob('request-net/{}-features/*.features'.format(dataset))
    
    node_names = set()
    request_types = set()
    
    for feature_filename in feature_filenames:
        with open(feature_filename, 'r') as fd:
            lines = fd.read().splitlines()
        request_types.add(lines[0])
        node_names.update(lines[1:])

    node_names = sorted(list(node_names))
    request_types = sorted(list(request_types))

    return node_names, request_types
    
