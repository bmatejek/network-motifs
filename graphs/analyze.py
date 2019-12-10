import math
import statistics



import networkx as nx



from networkx.algorithms import isomorphism



from network_motifs.graphs.construct import ConstructGraphFromTrace



def AnalyzeNodeSequences(traces):
    """
    Analyze the node sequences in the set of traces. Each trace set should
    correspond to a unique dataset + request type. Compares durations with and
    without the particular sequence present, as well as sequence specific stats.
    @param traces: the list of traces to analyze node sequences
    """
    # create a list of unique sequences for this request/trace
    sequences = set()
    for trace in traces:
        for sequence in trace.sequences:
            sequences.add(sequence.SequenceTuple())

    # create a mapping from sequences to indices
    sequences = list(sequences)
    sequence_mapping = {}
    for index, sequence in enumerate(sequences):
        sequence_mapping[sequence] = index

    # find distribution of sequences over traces
    nsequences = len(sequences)
    durations_for_sequences = [[] for _ in range(nsequences)]
    trace_durations_with_sequence = [[] for _ in range(nsequences)]
    trace_durations_without_sequence = [[] for _ in range(nsequences)]
    for trace in traces:
        contains_sequence = [False for _ in range(nsequences)]
        # find all sequences in this trace
        for sequence in trace.sequences:
            sequence_index = sequence_mapping[sequence.SequenceTuple()]
            durations_for_sequences[sequence_index].append(sequence.duration)
            contains_sequence[sequence_index] = True
        # iterate over sequences that occurred at least once or not at all
        for iv in range(nsequences):
            if contains_sequence[iv]:
                trace_durations_with_sequence[iv].append(trace.duration)
            else:
                trace_durations_without_sequence[iv].append(trace.duration)

    # get statistics for each sequence in the set of traces
    for iv in range(nsequences):
        # duration distribution for this sequence
        noccurrences = len(durations_for_sequences[iv])
        avg_sequence_duration = statistics.mean(durations_for_sequences[iv])
        stddev_sequence_duration = statistics.pstdev(durations_for_sequences[iv])

        # duration distribution for traces with this sequence
        no_traces_with_sequence = len(trace_durations_with_sequence[iv])
        avg_duration_with_sequence = statistics.mean(trace_durations_with_sequence[iv])
        stddev_duration_with_sequence = statistics.pstdev(trace_durations_with_sequence[iv])

        # duration distribution for traces without this sequence
        no_traces_without_sequence = len(trace_durations_without_sequence[iv])
        # skip traces where the sequence occurs in every trace
        if not no_traces_without_sequence: continue
        avg_duration_without_sequence = statistics.mean(trace_durations_without_sequence[iv])
        stddev_duration_without_sequence = statistics.pstdev(trace_durations_without_sequence[iv])

        # length of this sequence
        sequence_length = len(sequences[iv])

        # print out the statistics for this sequence
        print ('{} & {} & {:0.2f} ($\pm$ {:0.2f}) & {} & {:0.2f} ($\pm$ {:0.2f}) & {} & {:0.2f} ($\pm$ {:0.2f}) \\\\'.format(
            sequence_length, noccurrences, avg_sequence_duration, stddev_sequence_duration,
            no_traces_with_sequence, avg_duration_with_sequence, stddev_duration_with_sequence,
            no_traces_without_sequence, avg_duration_without_sequence, stddev_duration_without_sequence))



def FindUniqueTopologies(traces):
    """
    Find all of the unique topologies within this set of traces. A unique topology
    either differs in graph structure (parent/child) or function called at a node.
    @param traces: the list of traces to compare topologies
    """

    # node labels must match
    node_match = isomorphism.numerical_node_match('label', None)

    unique_graphs = []

    for trace in traces:
        graph_from_trace = ConstructGraphFromTrace(trace)

        # see if this matches any exists graphs
        unique_graph = True
        for iv in range(len(unique_graphs)):
            (durations, graph) = unique_graphs[iv]

            if nx.is_isomorphic(graph_from_trace, graph):
                durations.append(trace.duration)
                unique_graphs[iv] = (durations, graph)
                unique_graph = False
                break

        # create new entry for unique graph
        if unique_graph:
            unique_graphs.append(([trace.duration], graph_from_trace))

    # print statistics for the graph
    for (durations, graph) in unique_graphs:
        ntraces = len(durations)
        avg_duration = statistics.mean(durations)
        stddev_duration = statistics.pstdev(durations)

        print ('{} & {:0.2f} ($\pm$ {:0.2f})'.format(ntraces, avg_duration, stddev_duration))
