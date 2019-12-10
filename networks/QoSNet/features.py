import math
import struct
import statistics


import numpy as np



from network_motifs.motifs.constants import min_motif_size, max_motif_size
from network_motifs.utilities import dataIO
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
        trace_motifs = dataIO.ReadMotifs(dataset, trace, pruned=False)

        for motif in trace_motifs.motifs:
            motif_name = motif.sequence
            motif_duration = motif.duration

            # add to the list of motifs
            if not motif_name in motif_occurrences:
                motif_occurrences[motif_name] = []
            motif_occurrences[motif_name].append(motif_duration)

    # calculate statistics for all motifs
    average_motifs_durations = {}
    stddev_motif_durations = {}

    # get the average duration and standard deviation
    for motif in motif_occurrences:
        nmotif_occurrences = len(motif_occurrences[motif])

        average_motifs_durations[motif] = statistics.mean(motif_occurrences[motif])
        stddev_motif_durations[motif] = statistics.pstdev(motif_occurrences[motif])

    # add to the list of trace statistics
    trace_statistics['average-duration-per-motif'] = average_motifs_durations
    trace_statistics['stddev-duration-per-motif'] = stddev_motif_durations

    return trace_statistics



def PopulateFeatureVectors(dataset, trace, trace_statistics, with_motifs):
    # go through every node in the trace
    request_type = trace.request_type
    trace_motifs = dataIO.ReadMotifs(dataset, trace, pruned=True)
    motifs = trace_motifs.motifs
    nmotif_sizes = max_motif_size - min_motif_size + 1

    average_duration = trace_statistics['average-duration']
    stddev_duration = trace_statistics['stddev-duration']

    # zscore is what we are trying to predict
    completion_time = 10 * (trace.duration - average_duration) / stddev_duration

    # create a feature filename for writing
    if with_motifs: feature_filename = 'networks/QoSNet/features/{}/{}-with-motifs.features'.format(dataset, trace.base_id)
    else: feature_filename = 'networks/QoSNet/features/{}/{}.features'.format(dataset, trace.base_id)

    fd = open(feature_filename, 'wb')
    nnodes = len(trace.ordered_nodes)
    fd.write(struct.pack('i', nnodes))
    if with_motifs:
        nfeatures_per_node = 6 + 3 * nmotif_sizes
    else:
        nfeatures_per_node = 6
    fd.write(struct.pack('i', nfeatures_per_node))

    # keep track of the index for motifs
    motif_index = 0
    motif_stddev_below = {}
    motif_stddev_mid = {}
    motif_stddev_above = {}

    for iv in range(min_motif_size, max_motif_size + 1):
        motif_stddev_below[iv] = 0
        motif_stddev_mid[iv] = 0
        motif_stddev_above[iv] = 0

    # go through all of the nodes and create a feature
    for index, node in enumerate(trace.ordered_nodes):
        # how many motifs are completed before this node
        while motif_index < len(motifs) and motifs[motif_index].end_index <= index:
            # keep track of those whose durations are less than average, average, or more than average
            motif = motifs[motif_index]

            # get the stats for this motif
            average_duration = trace_statistics['average-duration-per-motif'][motif.sequence]
            stddev_duration = trace_statistics['stddev-duration-per-motif'][motif.sequence]
            if stddev_duration == 0.0:
                zscore = 0.0
            else:
                zscore = (motif.duration - average_duration) / stddev_duration
            motif_size = motifs[motif_index].motif_size

            if zscore < -2:
                motif_stddev_below[motif_size] += 1
            elif zscore < 2:
                motif_stddev_mid[motif_size] += 1
            else:
                motif_stddev_above[motif_size] += 1

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
        if with_motifs:
            for k in range(min_motif_size, max_motif_size + 1):
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




def ReadFeatures(dataset, trace_filenames, with_motifs):
    # create the list of features
    dataset_features = []
    dataset_labels = []

    for trace_filename in trace_filenames:
        base_id = trace_filename.split('/')[-1].split('.')[0]

        if with_motifs: feature_filename = 'networks/QoSNet/features/{}/{}-with-motifs.features'.format(dataset, base_id)
        else: feature_filename = 'networks/QoSNet/features/{}/{}.features'.format(dataset, base_id)

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

    # return the features and labels
    return dataset_features, dataset_labels



def Generate(datasets):
    # generate the features for QoS net for these datasets
    for dataset in datasets:
        for request_type in request_types_per_dataset[dataset]:
            training_traces = dataIO.ReadTrainingTraces(dataset, request_type)

            validation_traces = dataIO.ReadValidationTraces(dataset, request_type)

            testing_traces = dataIO.ReadTestingTraces(dataset, request_type)

            # only use the training and validation sets(?) to get statistics
            print ('{} {}'.format(dataset, request_type))
            trace_statistics = GenerateStatistics(dataset, training_traces)

            traces = training_traces + validation_traces + testing_traces

            for trace in traces:
                # populate feature vectors both with and without motif features
                PopulateFeatureVectors(dataset, trace, trace_statistics, True)
                PopulateFeatureVectors(dataset, trace, trace_statistics, False)
