from network_motifs.utilities import dataIO
from network_motifs.motifs.identify import ConvertTracesToSequenceArrays
from network_motifs.motifs.motif import Motif, Motifs



def HardMotifs(dataset, motifs_per_request_type):
    filenames = dataIO.ReadFilenames(dataset)

    min_motif_size = 2 ** 32
    max_motif_size = 0

    for request_type in motifs_per_request_type:
        for motif in motifs_per_request_type[request_type]:
            motif_size = len(motif)
            if motif_size > max_motif_size:
                max_motif_size = motif_size
            if motif_size < min_motif_size:
                min_motif_size = motif_size

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
                if not motif in motifs: continue

                start_index = iv2
                end_index = iv1
                duration = trace.ordered_nodes[end_index].timestamp - trace.ordered_nodes[start_index].timestamp
                assert (duration >= 0)

                queried_motifs.append(Motif(motif, start_index, end_index, duration))

        # create the motifs for this trace
        motifs_in_trace = Motifs(dataset, trace, queried_motifs)
        motifs_in_trace.WriteToFile(dataset)
