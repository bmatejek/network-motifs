import os
import math
import time
import struct
import statistics


import numpy as np



from network_motifs.motifs.motif import ReadMotifs
from network_motifs.utilities.dataIO import ReadTrainingTraces, ReadValidationTraces, ReadTestingTraces
from network_motifs.utilities.constants import request_types_per_dataset



def GenerateStatistics(dataset, traces):
    trace_statistics = {}

    # keep track of durations and nodes
    durations = []
    nnodes = []
    for trace in traces:
        durations.append(trace.duration)
        nnodes.append(len(trace.nodes))

    # add to the list of trace_statistics
    trace_statistics['average-duration'] = statistics.mean(durations)
    trace_statistics['stddev-duration'] = statistics.pstdev(durations)
    trace_statistics['average-nnodes'] = statistics.mean(nnodes)
    trace_statistics['stddev-nnodes'] = statistics.pstdev(nnodes)
    # give some standard deviation
    if trace_statistics['stddev-nnodes'] == 0.0:
        trace_statistics['stddev-nnodes'] = 1e-6

    # get distributions until start times
    max_nodes = max(nnodes)
    durations_until_time = [[] for _ in range(max_nodes)]
    for trace in traces:
        for iv, node in enumerate(trace.ordered_nodes):
            # get the amount of time from the start for this node
            time_from_start = node.timestamp - trace.minimum_timestamp
            durations_until_time[iv].append(time_from_start)

    # get distribution information at each node index
    average_time_until_node = []
    stddev_time_until_node = []
    for iv in range(max_nodes):
        average_time_until_node.append(statistics.mean(durations_until_time[iv]))
        stddev_time_until_node.append(statistics.pstdev(durations_until_time[iv]))

    # add to the list of trace_statistics
    trace_statistics['average-time-until-node'] = average_time_until_node
    trace_statistics['stddev-time-until-node'] = stddev_time_until_node

    motif_occurrences = {}

    # go through all traces and read the motifs
    for trace in traces:
        motifs = ReadMotifs(dataset, trace, 'fuzzy-collapsed-complete')

        for motif in motifs:
            motif_index = motif.motif_index
            motif_duration = motif.duration

            # add to the list of motifs
            if not motif_index in motif_occurrences:
                motif_occurrences[motif_index] = []
            motif_occurrences[motif_index].append(motif_duration)

    # calculate statistics for all motifs
    average_motifs_durations = {}
    stddev_motif_durations = {}

    # get the average duration and standard deviation
    for motif_index in motif_occurrences:
        average_motifs_durations[motif_index] = statistics.mean(motif_occurrences[motif_index])
        stddev_motif_durations[motif_index] = statistics.pstdev(motif_occurrences[motif_index])

    # add to the list of trace statistics
    trace_statistics['average-duration-per-motif'] = average_motifs_durations
    trace_statistics['stddev-duration-per-motif'] = stddev_motif_durations

    return trace_statistics



def PopulateFeatureVectors(dataset, trace, trace_statistics):
    # go through every node in the trace
    request_type = trace.request_type
    motifs = ReadMotifs(dataset, trace, 'fuzzy-collapsed-pruned')

    average_duration = trace_statistics['average-duration']
    stddev_duration = trace_statistics['stddev-duration']

    # zscore is what we are trying to predict
    completion_time = 10 * (trace.duration - average_duration) / stddev_duration

    # create a feature filename for writing
    feature_filename = 'networks/QoSNet/features/{}/{}.features'.format(dataset, trace.base_id)

    fd = open(feature_filename, 'wb')
    nnodes = len(trace.ordered_nodes)
    fd.write(struct.pack('i', nnodes))
    nfeatures_per_node = 6 + 9
    fd.write(struct.pack('i', nfeatures_per_node))

    # keep track of the index for motifs
    motif_index = 0
    motif_stddev_below = [0 for iv in range(3)]
    motif_stddev_mid = [0 for iv in range(3)]
    motif_stddev_above = [0 for iv in range(3)]

    # go through all of the nodes and create a feature
    for index, node in enumerate(trace.ordered_nodes):
        # how many motifs are completed before this node
        while motif_index < len(motifs) and motifs[motif_index].maximum_timestamp <= node.timestamp:
            # keep track of those whose durations are less than average, average, or more than average
            motif = motifs[motif_index]

            average_duration = trace_statistics['average-duration-per-motif'][motif.motif_index]
            stddev_duration = trace_statistics['stddev-duration-per-motif'][motif.motif_index]
            if stddev_duration == 0.0:
                zscore = 0.0
            else:
                zscore = (motif.duration - average_duration) / stddev_duration
            motif_size = motifs[motif_index].size()

            # divide into three sizes, small, medium, large
            if motif_size < 6:
                motif_size_index = 0
            elif motif_size < 9:
                motif_size_index = 1
            else:
                motif_size_index = 2

            if zscore < -2:
                motif_stddev_below[motif_size_index] += 1
            elif zscore < 2:
                motif_stddev_mid[motif_size_index] += 1
            else:
                motif_stddev_above[motif_size_index] += 1

            motif_index += 1

        # write the average and stddev number of nodes per this request
        average_nnodes = trace_statistics['average-nnodes']
        stddev_nodes = trace_statistics['stddev-nnodes']

        fd.write(struct.pack('ff', average_nnodes, stddev_nodes))
        # write the index of this node
        ratio_to_average = index / average_nnodes
        index_zscore = (index - average_nnodes) / stddev_nodes
        fd.write(struct.pack('fff', index, ratio_to_average, index_zscore))
        # write the time until the start, the average time, stddev, and zscore
        current_duration = node.timestamp - trace.minimum_timestamp
        if index >= len(trace_statistics['average-time-until-node']):
            average_duration_to_index = current_duration
            stddev_duration_to_index = 0.0
        else:
            average_duration_to_index = trace_statistics['average-time-until-node'][index]
            stddev_duration_to_index = trace_statistics['stddev-time-until-node'][index]
        if stddev_duration_to_index == 0.0: duration_zscore = 0.0
        else: duration_zscore = (current_duration - average_duration_to_index) / stddev_duration_to_index
        #fd.write(struct.pack('ffff', average_duration_to_index, stddev_duration_to_index, current_duration, duration_zscore))
        fd.write(struct.pack('f', duration_zscore))

        # write the stats for motifs of size k
        for k in range(3):
            nbelow = motif_stddev_below[k]
            nmid = motif_stddev_mid[k]
            nabove = motif_stddev_above[k]
            total_motifs = nbelow + nmid + nabove

            if total_motifs == 0:
                fd.write(struct.pack('fff', nbelow, nmid, nabove))
            else:
                fd.write(struct.pack('fff', nbelow / total_motifs, nmid / total_motifs, nabove / total_motifs))

        # write the label we are trying to predict
        fd.write(struct.pack('f', completion_time))



def ReadFeatures(dataset, trace_filenames):
    # create the list of features
    dataset_features = []
    dataset_labels = []

    nnodes_per_feature = []

    for trace_filename in trace_filenames:
        base_id = trace_filename.split('/')[-1].split('.')[0]

        feature_filename = 'networks/QoSNet/features/{}/{}.features'.format(dataset, base_id)


        with open(feature_filename, 'rb') as fd:
            nnodes, nfeatures_per_node, = struct.unpack('ii', fd.read(8))

            for iv in range(nnodes):
                features = np.zeros(nfeatures_per_node, dtype=np.float32)
                for ii in range(nfeatures_per_node):
                    features[ii], = struct.unpack('f', fd.read(4))

                # read the label we are trying to predict
                label, = struct.unpack('f', fd.read(4))

                dataset_features.append(features)
                dataset_labels.append(label)
                nnodes_per_feature.append(nnodes)

    # return the features and labels
    return dataset_features, dataset_labels, nnodes_per_feature



def Generate(datasets):
    # create directory structure if it does not exist
    if not os.path.exists('networks'):
        os.mkdir('networks')
    if not os.path.exists('networks/QoSNet'):
        os.mkdir('networks/QoSNet')
    if not os.path.exists('networks/QoSNet/features/'):
        os.mkdir('networks/QoSNet/features/')


    # generate the features for QoS net for these datasets
    for dataset in datasets:
        if not os.path.exists('networks/QoSNet/features/{}'.format(dataset)):
            os.mkdir('networks/QoSNet/features/{}'.format(dataset))
        for request_type in request_types_per_dataset[dataset]:
            # start statistics
            start_time = time.time()

            training_traces = ReadTrainingTraces(dataset, request_type)

            validation_traces = ReadValidationTraces(dataset, request_type)

            testing_traces = ReadTestingTraces(dataset, request_type)

            # only use the training and validation sets(?) to get statistics
            print ('{} {}'.format(dataset, request_type))
            trace_statistics = GenerateStatistics(dataset, training_traces)

            traces = training_traces + validation_traces + testing_traces

            for trace in traces:
                # populate feature vectors both with and without motif features
                PopulateFeatureVectors(dataset, trace, trace_statistics)

            # print statistics
            print('Generated features for {} {} in {:0.2f} seconds'.format(dataset, request_type, time.time() - start_time))
