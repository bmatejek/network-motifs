from network_motifs.utilities import dataIO
from network_motifs.motifs.identify import ConvertTracesToSequenceArrays
from network_motifs.motifs.motif import Motif, Motifs
from network_motifs.motifs.constants import min_motif_size, max_motif_size



def PruneMotifs(queried_motifs):
    # sort the motifs first by start index and then by size (use -1 so large motifs are first)
    queried_motifs = sorted(queried_motifs, key = lambda x : (x.start_index, -1 * x.motif_size))
    # create a list of pruned motifs
    pruned_motifs = []
    # create the list of nodes that are already associated with a motif
    claimed_nodes = set()

    # go through each found motif
    for queried_motif in queried_motifs:
        # get the elements that belong to this motif
        nodes = [iv for iv in range(queried_motif.start_index, queried_motif.end_index + 1)]
        # see if this motif can be added
        allow_motif = True
        for node in nodes:
            if node in claimed_nodes: allow_motif = False
        if not allow_motif: continue
        # add the motif and remove nodes from allowable list
        pruned_motifs.append(queried_motif)
        for node in nodes:
            claimed_nodes.add(node)

    return pruned_motifs



def HardMotifs(dataset, motifs_per_request_type):
    filenames = dataIO.ReadFilenames(dataset)

    for filename in filenames:
        trace = dataIO.ReadTrace(dataset, filename)

        # get the motifs for this request type
        motifs = motifs_per_request_type[trace.request_type]

        # keep track of the motifs found in this trace
        queried_motifs = []

        # convert this trace into an integer sequence
        sequence_array = ConvertTracesToSequenceArrays(dataset, [trace])[0]
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

                # is this a valid motif?
                if not key in motifs: continue

                start_index = iv2
                end_index = iv1
                duration = trace.ordered_nodes[end_index].timestamp - trace.ordered_nodes[start_index].timestamp
                assert (duration >= 0)

                queried_motifs.append(Motif(key, start_index, end_index, duration))

        # write the queried motifs to file
        motifs_in_trace = Motifs(dataset, trace, queried_motifs)
        motifs_in_trace.WriteToFile(dataset, False)

        # prune the motifs so that each node has at most one motif
        pruned_motifs = PruneMotifs(queried_motifs)
        # create the motifs for this trace
        motifs_in_trace = Motifs(dataset, trace, pruned_motifs)
        motifs_in_trace.WriteToFile(dataset, True)
