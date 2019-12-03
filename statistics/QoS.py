import math
import struct



from network_motifs.utilities import dataIO



def GenerateQoSThresholds(dataset):
    # read in all of the training traces
    training_filenames = dataIO.ReadTrainingFilenames(dataset)

    # read in all of the traces
    traces = []
    for training_filename in training_filenames:
        traces.append(dataIO.ReadTrace(dataset, training_filename))

    # get all of the durations for the datasets
    durations = {}
    for trace in traces:
        if not trace.request_type in durations:
            durations[trace.request_type] = []

        durations[trace.request_type].append(trace.duration)

    avg_duration = {}
    QoS_threshold = {}
    for request_type in durations:
        durations[request_type] = sorted(durations[request_type])
        ntraces = len(durations[request_type])
        avg_duration[request_type] = sum(durations[request_type]) / ntraces
        # get the threshold for QoS violation
        index = int(math.floor(0.9 * ntraces))
        QoS_threshold[request_type] = durations[request_type][index]
    stddev_duration = {}
    for request_type in durations:
        ntraces = len(durations[request_type])
        stddev_duration[request_type] = 0.0
        for duration in durations[request_type]:
            stddev_duration[request_type] += (avg_duration[request_type] - duration) ** 2
        stddev_duration[request_type] = math.sqrt(stddev_duration[request_type] / (ntraces - 1))

    for request_type in durations:
        filename = 'statistics/QoS-{}-{}.stat'.format(dataset, request_type)
        with open(filename, 'wb') as fd:
            fd.write(struct.pack('fff', avg_duration[request_type], stddev_duration[request_type], QoS_threshold[request_type]))
