from network_motifs.utilities import dataIO



def CreateNameMapping(dataset):
    filenames = dataIO.ReadFilenames(dataset)

    # create a set of all possible function names
    names = set()

    # go through all files in this dataset
    for filename in filenames:
        trace = dataIO.ReadTrace(dataset, filename)

        names = names | trace.UniqueNames()

    names = sorted(list(names))

    output_filename = 'mappings/{}/name-to-index.txt'.format(dataset)
    with open(output_filename, 'w') as fd:
        for name in names:
            fd.write('{}\n'.format(name))
