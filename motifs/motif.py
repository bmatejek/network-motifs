import struct



class Motifs(object):
    def __init__(self, dataset, trace, motifs):
        self.dataset = dataset
        self.trace = trace
        self.motifs = motifs

    def WriteToFile(self, dataset):
        motif_filename = 'motifs/{}/{}.motifs'.format(dataset, self.trace.base_id)

        with open(motif_filename, 'wb') as fd:
            nmotifs = len(self.motifs)
            fd.write(struct.pack('i', nmotifs))
            for motif in self.motifs:
                # write this motif to this file location
                fd.write(struct.pack('i', motif.motif_size))
                for iv in range(motif.motif_size):
                    fd.write(struct.pack('i', motif.motif[iv]))
                fd.write(struct.pack('iiq', motif.start_index, motif.end_index, motif.duration))



class Motif(object):
    def __init__(self, motif, start_index, end_index, duration):
        self.motif_size = len(motif)
        self.motif = motif
        self.start_index = start_index
        self.end_index = end_index
        self.duration = duration
