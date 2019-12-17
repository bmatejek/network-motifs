import time
import statistics



from network_motifs.motifs.motif import ReadMotifs
from network_motifs.utilities.dataIO import ReadTraces



def CompareMotifMethods(dataset, request_type):
    """
    Compare the various methods for generating motifs for various statistics.
    @params dataset: the dataset that contains all of the traces
    @params request_type: the type of request that we have for this data combo
    """
    # start_statistics
    start_time = time.time()

    # motif methods have the following suffixes
    suffixes = ['complete', 'collapsed-complete', 'fuzzy-collpased-complete',
                'pruned', 'collapsed-pruned', 'fuzzy-collapsed-pruned']

    # read all of the relevant traces
    traces = ReadTraces(dataset, request_type, None)
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

        # print the statistics for this motif method
        print (suffix)
        print ('{:0.2f} ($\pm${:0.2f}) & {} & {:0.2f} ($\pm${:0.2f}) & {:0.2f} ($\pm${:0.2f})'.format(
                                                statistics.mean(motifs_per_trace),
                                                statistics.pstdev(motifs_per_trace),
                                                len(unique_motifs),
                                                statistics.mean(motif_sizes),
                                                statistics.pstdev(motif_sizes),
                                                statistics.mean(coverages),
                                                statistics.pstdev(coverages)
                                                ))

    # print statistics
    print ('Generated statistics for {} {} in {:0.2f} seconds.'.format(dataset, request_type, time.time() - start_time))
