import os
import math
import struct
import statistics



from network_motifs.utilities.dataIO import ReadTrainingTraces
from network_motifs.utilities.constants import request_types_per_dataset



def GenerateQoSThresholds(dataset):
    if not os.path.exists('statistics'):
        os.mkdir('statistics')


    for request_type in request_types_per_dataset[dataset]:
        traces = ReadTrainingTraces(dataset, request_type)
        durations = []
        for trace in traces:
            durations.append(trace.duration)

        avg_duration = statistics.mean(durations)
        stddev_duration = statistics.pstdev(durations)
        QoS_threshold = avg_duration + stddev_duration

        filename = 'statistics/QoS-{}-{}.stat'.format(dataset, request_type)
        with open(filename, 'wb') as fd:
            fd.write(struct.pack('fff', avg_duration, stddev_duration, QoS_threshold))
