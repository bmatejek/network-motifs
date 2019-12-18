import statistics



from network_motifs.motifs.motif import ReadMotifs
from network_motifs.motifs.query import IdentifyFrequentSubgraphs
from network_motifs.utilities.dataIO import ReadTraces



def CompareMotifMethods(dataset):
    """
    Compare the various methods for generating motifs for various statistics.
    @params dataset: the dataset that contains all of the traces
    """
    # motif methods have the following suffixes
    suffixes = ['complete', 'collapsed-complete', 'fuzzy-collapsed-complete',
                'pruned', 'collapsed-pruned', 'fuzzy-collapsed-pruned']

    suffix_human_readable = {
        'complete': 'Exhaustive Motifs',
        'collapsed-complete': 'Exhaustive Sequence Reduced',
        'fuzzy-collapsed-complete': 'Exhaustive Fuzzy Sequence Reduced',
        'pruned': 'Pruned Motifs',
        'collapsed-pruned': 'Pruned Sequence Reduced',
        'fuzzy-collapsed-pruned': 'Pruned Fuzzy Sequence Reduced',

    }

    print ('{}'.format(dataset))

    # read all of the relevant traces
    traces = ReadTraces(dataset, None, None)
    # get the statistics for this suffix
    for suffix in suffixes:
        motifs_per_trace = []
        unique_motifs = set()
        motif_sizes = []
        coverages = []
        for trace in traces:
            # read the motifs for this trace
            motifs = ReadMotifs(dataset, trace, suffix)
            nnodes = len(trace.nodes)

            nodes_covered = [False for _ in range(nnodes)]

            # add all of the relevant stats
            motifs_per_trace.append(len(motifs))
            for motif in motifs:
                unique_motifs.add(motif.motif_index)
                motif_sizes.append(motif.size())
                for node in motif.nodes:
                    nodes_covered[node.index] = True

            coverages.append(100 * sum(nodes_covered) / nnodes)

        if not len(motif_sizes): continue
        max_motif_size = max(motif_sizes)
        # print the statistics for this motif method
        print ('{} & {:0.2f} ($\pm${:0.2f}) & {} & {:0.2f} ($\pm${:0.2f}) & {:0.2f} ($\pm${:0.2f}) & {}'.format(
                                                suffix_human_readable[suffix],
                                                statistics.mean(motifs_per_trace),
                                                statistics.pstdev(motifs_per_trace),
                                                len(unique_motifs),
                                                statistics.mean(motif_sizes),
                                                statistics.pstdev(motif_sizes),
                                                statistics.mean(coverages),
                                                statistics.pstdev(coverages),
                                                max_motif_size
                                                ))
    print ('\n')
