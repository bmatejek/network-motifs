import math
import struct


import numpy as np



from network_motifs.data_structures.trace import GetUniqueRequestTypes
from network_motifs.utilities import dataIO



def GenerateStatistics(dataset, traces):
    statistics = {}

    # get the average duration and standard deviation
    average_duration = 0.0
    for trace in traces:
        average_duration += trace.duration
    average_duration /= len(traces)
    stddev_duration = 0.0
    for trace in traces:
        stddev_duration += (trace.duration - average_duration) ** 2
    stddev_duration = math.sqrt(stddev_duration) / (len(traces) - 1)

    statistics['average-duration'] = average_duration
    statistics['stddev-duration'] = stddev_duration

    # get the average number of nodes for this request type
    average_nnodes = 0.0
    max_nodes = 0
    for trace in traces:
        average_nnodes += len(trace.nodes)
        if len(trace.nodes) > max_nodes: max_nodes = len(trace.nodes)
    average_nnodes /= len(traces)
    stddev_nnodes = 0.0
    for trace in traces:
        stddev_nnodes += (len(trace.nodes) - average_nnodes) ** 2
    stddev_nodes = math.sqrt(stddev_nnodes) / (len(trace.nodes) - 1)

    statistics['average-nnodes'] = average_nnodes
    statistics['stddev-nnodes'] = stddev_nnodes

    # get the average duration and standard deviation for each node
    average_time_until_node = [0.0 for _ in range(max_nodes)]
    ntraces_for_average_times = [0 for _ in range(max_nodes)]
    for trace in traces:
        for iv, node in enumerate(trace.ordered_nodes):
            # the amount of time from start to this nodes appearance
            time_from_start = node.timestamp - trace.minimum_timestamp
            average_time_until_node[iv] += time_from_start
            ntraces_for_average_times[iv] += 1
    for iv in range(max_nodes):
        average_time_until_node[iv] /= ntraces_for_average_times[iv]
    stddev_time_until_node = [0.0 for _ in range(max_nodes)]
    for trace in traces:
        for iv, node in enumerate(trace.ordered_nodes):
            # the amount of time from start to this nodes appearance
            time_from_start = node.timestamp - trace.minimum_timestamp
            stddev_time_until_node[iv] += (time_from_start - average_time_until_node[iv]) ** 2
    for iv in range(max_nodes):
        if ntraces_for_average_times[iv] == 1:
            stddev_time_until_node[iv] = 0.0
        else:
            stddev_time_until_node[iv] = math.sqrt(stddev_time_until_node[iv]) / (ntraces_for_average_times[iv] - 1)

    statistics['average-time-until-node'] = average_time_until_node
    statistics['stddev-time-until-node'] = stddev_time_until_node

    motif_occurrences = {}

    # go through all traces and read the motifs
    for trace in traces:
        trace_motifs = dataIO.ReadMotifs(dataset, trace)

        for motif in trace_motifs.motifs:
            motif_name = motif.motif
            motif_duration = motif.duration

            # add to the list of motifs
            if not motif_name in motif_occurrences:
                motif_occurrences[motif_name] = []
            motif_occurrences[motif_name].append(motif_duration)

    # calculate statistics for all motifs
    average_motifs_durations = {}
    stddev_motif_durations = {}

    # get the average duration and standard deviation
    for motif in average_motifs_durations:
        nmotif_occurrences = len(motif_occurrences[motif])
        average_duration = sum(motif_occurrences[motif]) / nmotif_occurrences
        stddev_duration = 0.0
        for duration in motif_occurrences[motif]:
            stddev_duration += (duration - average_duration) ** 2
        stddev_duration = math.sqrt(stddev_duration) / (nmotif_occurrences - 1)

        average_motifs_durations[motif] = average_duration
        stddev_motif_durations[motif] = stddev_duration

    statistics['average-duration-per-motif'] = average_motifs_durations
    statistics['stddev-duration-per-motif'] = stddev_motif_durations

    return statistics



def PopulateFeatureVectors(dataset, trace, statistics):
    # go through every node in the trace
    request_type = trace.request_type
    motifs = dataIO.ReadMotifs(dataset, trace)

    average_duration = statistics['average-duration']
    stddev_duration = statistics['stddev-duration']

    # zscore is what we are trying to predict
    completion_time = (trace.duration - average_duration) / stddev_duration

    # create a feature filename for writing
    feature_filename = 'networks/QoSNet/features/{}/{}.features'.format(dataset, trace.base_id)
    fd = open(feature_filename, 'wb')
    nnodes = len(trace.ordered_nodes)
    fd.write(struct.pack('i', nnodes))
    nfeatures_per_node = 6
    fd.write(struct.pack('i', nfeatures_per_node))

    # go through all of the nodes and create a feature
    for index, node in enumerate(trace.ordered_nodes):
        # write the average and stddev number of nodes per this request
        average_nnodes = statistics['average-nnodes']
        stddev_nodes = statistics['stddev-nnodes']
        fd.write(struct.pack('ff', average_nnodes, stddev_nodes))
        # write the index of this node
        ratio_to_average = index / average_nnodes
        index_zscore = (index - average_nnodes) / stddev_nodes
        fd.write(struct.pack('fff', index, ratio_to_average, index_zscore))
        # write the time until the start, the average time, stddev, and zscore
        current_duration = node.timestamp - trace.minimum_timestamp
        if index >= len(statistics['average-time-until-node']):
            average_duration_to_index = current_duration
            stddev_duration_to_index = 0.0
        else:
            average_duration_to_index = statistics['average-time-until-node'][index]
            stddev_duration_to_index = statistics['stddev-time-until-node'][index]
        if stddev_duration_to_index == 0.0: duration_zscore = 0.0
        else: duration_zscore = (current_duration - average_duration_to_index) / stddev_duration_to_index
        #fd.write(struct.pack('ffff', average_duration_to_index, stddev_duration_to_index, current_duration, duration_zscore))
        fd.write(struct.pack('f', duration_zscore))

        # write the label we are trying to predict
        fd.write(struct.pack('f', completion_time))



def ReadFeatures(dataset, trace_filenames):
    # create the list of features
    dataset_features = []
    dataset_labels = []

    for trace_filename in trace_filenames:
        base_id = trace_filename.split('/')[-1].split('.')[0]

        feature_filename = 'networks/QoSNet/features/{}/{}.features'.format(dataset, base_id)
        with open(feature_filename, 'rb') as fd:
            nnodes, nfeatures_per_node, = struct.unpack('ii', fd.read(8))
            for iv in range(nnodes):
                features = np.zeros(nfeatures_per_node, dtype=np.float32)
                # read the average and stddev number of nodes per this request
                features[0], features[1], = struct.unpack('ff', fd.read(8))
                # read the index of this node
                features[2], features[3], features[4], = struct.unpack('fff', fd.read(12))
                # read the time until the start, the average time, stddev, and zscore
                #features[5], features[6], features[7], features[8], = struct.unpack('ffff', fd.read(16))
                features[5],  = struct.unpack('f', fd.read(4))
                # read the label we are trying to predict
                label, = struct.unpack('f', fd.read(4))

                dataset_features.append(features)
                dataset_labels.append(label)

    # return the features and labels
    return dataset_features, dataset_labels



def Generate(datasets):
    # generate the features for QoS net for these datasets
    for dataset in datasets:
        # get the filenames for each of the three subsets
        training_filenames = dataIO.ReadTrainingFilenames(dataset)
        training_traces_per_request_type = {}
        for training_filename in training_filenames:
            trace = dataIO.ReadTrace(dataset, training_filename)
            if not trace.request_type in training_traces_per_request_type:
                training_traces_per_request_type[trace.request_type] = []
            training_traces_per_request_type[trace.request_type].append(trace)

        validation_filenames = dataIO.ReadValidationFilenames(dataset)
        validation_traces_per_request_type = {}
        for validation_filename in validation_filenames:
            trace = dataIO.ReadTrace(dataset, validation_filename)
            if not trace.request_type in validation_traces_per_request_type:
                validation_traces_per_request_type[trace.request_type] = []
            validation_traces_per_request_type[trace.request_type].append(trace)

        testing_filenames = dataIO.ReadTestingFilenames(dataset)
        testing_traces_per_request_type = {}
        for testing_filename in testing_filenames:
            trace = dataIO.ReadTrace(dataset, testing_filename)
            if not trace.request_type in testing_traces_per_request_type:
                testing_traces_per_request_type[trace.request_type] = []
            testing_traces_per_request_type[trace.request_type].append(trace)

        # get the requests for this trace
        request_types = training_traces_per_request_type.keys()

        for request_type in request_types:
            training_traces = training_traces_per_request_type[request_type]
            validation_traces = validation_traces_per_request_type[request_type]
            testing_traces = testing_traces_per_request_type[request_type]

            # only use the training and validation sets(?) to get statistics
            print ('{} {}'.format(dataset, request_type))
            statistics = GenerateStatistics(dataset, training_traces)

            traces = training_traces + validation_traces + testing_traces

            for trace in traces:
                PopulateFeatureVectors(dataset, trace, statistics)
