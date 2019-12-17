import time



from network_motifs.motifs.motif import ReadMotifs, WriteMotifs
from network_motifs.utilities.dataIO import ReadTraces



def PruneMotifs(dataset, suffix):
    """
    Prune all the motifs in this dataset so that each node can belong to at
    most one motif. Motifs with earlier start indices and larger spans are
    prioritized.
    """
    # start statistics
    start_time = time.time()

    # read all of the traces for this dataset
    traces = ReadTraces(dataset, None, None)

    # iterate over all traces
    for trace in traces:
        # read the motifs for this trace dataset
        motifs = ReadMotifs(dataset, trace, suffix)

        pruned_motifs = []

        # all nodes start as uncovered
        nnodes = len(trace.nodes)
        nodes_covered = [False for _ in range(nnodes)]

        # sort the motifs by size and start timestamp
        motifs = sorted(motifs, reverse=True)

        # go through the motifs to identify valid ones
        for motif in motifs:
            prune_this_motif = False
            for node in motif.nodes:
                # if this node belongs to another motif remove it
                if nodes_covered[node.index]:
                    prune_this_motif = True
                    break
            if prune_this_motif: continue

            # all the nodes in this motif are now covered
            for node in motif.nodes:
                nodes_covered[node.index] = True

            # add the motif to the list of motifs
            pruned_motifs.append(motif)

        # save the motifs as pruned
        output_suffix = suffix.replace('complete', 'pruned')
        output_filename = 'motifs/subgraphs/{}/{}-motifs-{}.motifs'.format(dataset, trace.base_id, output_suffix)

        WriteMotifs(output_filename, pruned_motifs)

    # print statistics
    print ('Pruned motifs for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))
