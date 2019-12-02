import struct



class Motifs(object):
    def __init__(self, dataset, trace, motifs):
        self.dataset = dataset
        self.trace = trace
        # sort by end index of this motif
        self.motifs = sorted(motifs, key=lambda x : x.end_index)


    def WriteToFile(self, dataset, pruned):
        if pruned: motif_filename = 'motifs/{}/{}-pruned.motifs'.format(dataset, self.trace.base_id)
        else: motif_filename = 'motifs/{}/{}-queried.motifs'.format(dataset, self.trace.base_id)

        with open(motif_filename, 'wb') as fd:
            nmotifs = len(self.motifs)
            fd.write(struct.pack('i', nmotifs))
            for motif in self.motifs:
                # write this motif to this file location
                fd.write(struct.pack('i', motif.motif_size))
                for iv in range(motif.motif_size):
                    fd.write(struct.pack('i', motif.sequence[iv]))
                fd.write(struct.pack('iiq', motif.start_index, motif.end_index, motif.duration))



class Motif(object):
    def __init__(self, sequence, start_index, end_index, duration):
        self.motif_size = len(sequence)
        self.sequence = sequence
        self.start_index = start_index
        self.end_index = end_index
        self.duration = duration
