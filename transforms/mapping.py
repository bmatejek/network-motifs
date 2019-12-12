import os
import time


from network_motifs.utilities import dataIO



def CreateNameMapping(dataset):
    """
    Create a mapping between all of the names in the dataset and a unique ID.
    The mapping is called from the function GetUniqueNames in trace.py.
    @params dataset: the dataset for which to create the mapping
    """
    # start statistics
    start_time = time.time()

    # create the directories for the mappings
    if not os.path.exists('mappings'):
        os.mkdir('mappings')
    if not os.path.exists('mappings/{}'.format(dataset)):
        os.mkdir('mappings/{}'.format(dataset))

    filenames = dataIO.ReadFilenames(dataset)

    # create a set of all possible function names
    names = set()

    # go through all files in this dataset
    for filename in filenames:
        trace = dataIO.ReadTrace(dataset, filename)

        names = names | trace.UniqueNames()

    names = sorted(list(names))

    # output the mapping to disk
    output_filename = 'mappings/{}/name-to-index.txt'.format(dataset)
    with open(output_filename, 'w') as fd:
        for name in names:
            fd.write('{}\n'.format(name))

    # print statistics
    print ('Created function name mappings for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))
