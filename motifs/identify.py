import numpy as np



from network_motifs.data_structures.trace import GetUniqueNames
from network_motifs.utilities import dataIO



def ConvertTracesToSequenceArrays(dataset, traces):
    # create a mapping for node names to indices
    names, name_to_index, _ = GetUniqueNames(dataset)

    sequence_arrays = []

    # create an array for each trace
    for trace in traces:
        nnodes = len(trace.ordered_nodes)
        sequence_array = np.zeros(nnodes, dtype=np.int32)
        for iv, node in enumerate(trace.ordered_nodes):
            index = name_to_index[node.Name()]
            sequence_array[iv] = index

        # add this motif list
        sequence_arrays.append(sequence_array)

    return sequence_arrays



def FindHardMotifsByRequestType(dataset, traces):
    sequence_arrays = ConvertTracesToSequenceArrays(dataset, traces)

    # first find the most frequent hard motifs
    sequence_counts = {}
    # only consider motifs of a certain size
    max_motif_size = 20
    min_motif_size = 5

    nsequences = {}
    for motif_size in range(min_motif_size, max_motif_size + 1):
        nsequences[motif_size] = 0


    # look at all possible motifs for each trace
    ntraces = len(sequence_arrays)
    for it in range(ntraces):
        sequence_array = sequence_arrays[it]
        nnodes = sequence_array.size
        for iv1 in range(nnodes):
            # consider every possible motif to this node
            for iv2 in range(iv1 - max_motif_size, iv1 - min_motif_size + 1):
                if iv2 < 0: continue
                sequence = sequence_array[iv2:iv1]

                # convert the sequence into a tuple
                key = ()
                for seq in sequence:
                    key = key + (seq,)

                # add the key to the list of counts
                if not key in sequence_counts:
                    sequence_counts[key] = 1
                else:
                    sequence_counts[key] += 1

                # update the number of sequences of this length
                nsequences[len(key)] += 1

    # get the hard motifs for this request
    motifs = []

    # go through all motifs and look for high frequency ones
    for sequence in sequence_counts:
        # what is the size of this sequence
        nnodes_in_sequence = len(sequence)
        # how often did this sequence occur
        noccurrences = sequence_counts[sequence]
        # what is the frequency of this motif
        frequency = 100 * noccurrences / nsequences[len(sequence)]
        # only consider motifs with greater than 2% frequency or at least one occurrence per trace
        if frequency < 2 and noccurrences < len(traces): continue

        motifs.append(sequence)

    # return the motifs as a set
    return set(motifs)



def FindHardMotifs(dataset):
    # using the training datasets to identify high frequency motifs
    training_filenames = dataIO.ReadTrainValFilenames(dataset)
    training_traces_by_request_type = {}

    for filename in training_filenames:
        trace = dataIO.ReadTrace(dataset, filename)

        # separate the training data by request type for motif discovery
        if not trace.request_type in training_traces_by_request_type:
            training_traces_by_request_type[trace.request_type] = []
        training_traces_by_request_type[trace.request_type].append(trace)

    # read the testing filenames for motif query only
    testing_filenames = dataIO.ReadTestingFilenames(dataset)
    testing_traces_by_request_type = {}

    for filename in testing_filenames:
        trace = dataIO.ReadTrace(dataset, filename)

        # separate the testing data by request type for motif discovery
        if not trace.request_type in testing_traces_by_request_type:
            testing_traces_by_request_type[trace.request_type] = []
        testing_traces_by_request_type[trace.request_type].append(trace)

    motifs = {}

    # get the motifs for this request type
    for request_type in training_traces_by_request_type:
        motifs[request_type] = FindHardMotifsByRequestType(dataset, training_traces_by_request_type[request_type])

    return motifs
