from network_motifs.utilities import dataIO
from network_motifs.motifs.identify import ConvertTracesToSequenceArrays
from network_motifs.motifs.motif import Motif, Motifs
from network_motifs.motifs.constants import min_motif_size, max_motif_size



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

        # create the motifs for this trace
        motifs_in_trace = Motifs(dataset, trace, queried_motifs)
        motifs_in_trace.WriteToFile(dataset)
