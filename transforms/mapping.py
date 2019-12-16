import os
import json
import time
import difflib



from network_motifs.utilities import dataIO
from network_motifs.data_structures.unionfind import UnionFindElement, Find, Union
from network_motifs.data_structures.trace import GetUniqueNames, GetUniqueNodeSequences



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

    traces = dataIO.ReadTraces(dataset, None, None)

    # create a set of all possible function names
    names = set()

    # go through all files in this dataset
    for trace in traces:
        names = names | trace.UniqueNames()

    names = sorted(list(names))

    # output the mapping to disk
    output_filename = 'mappings/{}/name-to-index.txt'.format(dataset)
    with open(output_filename, 'w') as fd:
        for name in names:
            fd.write('{}\n'.format(name))

    # print statistics
    print ('Created function name mappings for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))



def CreateHardNodeSequenceMapping(dataset):
    """
    Create a mapping between node sequences in this dataset to a unique ID. This
    enables the sequences to collapse to a single node in a graph. The sequences
    need to be an exact match.
    @params dataset: the dataset for which to analyze node sequences
    """
    # start statistics
    start_time = time.time()

    # how many names are there and start the mapping at that index
    names_to_index = GetUniqueNames(dataset)
    nnames = len(names_to_index)

    # create the directories for the mappings
    if not os.path.exists('mappings'):
        os.mkdir('mappings')
    if not os.path.exists('mappings/{}'.format(dataset)):
        os.mkdir('mappings/{}'.format(dataset))

    # read all of the traces independent of request type
    traces = dataIO.ReadTraces(dataset, None, None)

    # create a set of all the unique sequences
    sequences = set()

    # go through every trace in the dataset
    for trace in traces:
        # go through every sequence in the dataset
        for sequence in trace.sequences:
            sequences.add(sequence.SequenceTuple())

    # sort the list
    sequences = sorted(list(sequences))

    # save the sequence to an output filename
    output_filename = 'mappings/{}/hard-node-sequence-to-index.txt'.format(dataset)
    with open(output_filename, 'w') as fd:
        nsequences = len(sequences)
        fd.write('{}\n'.format(nsequences))
        for iv, sequence in enumerate(sequences):
            sequence_length = len(sequence)
            fd.write('{}\n'.format(sequence_length))
            for node in sequence:
                fd.write('{}\n'.format(node))
            fd.write('{}\n'.format(iv + nnames))

    # print statistics
    print ('Created hard sequence name mappings for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))



def ConvertSequenceToUnicode(sequence, names_to_index):
    """
    Returns a unicode string from a sequence.
    @param sequence: the node sequence from a trace
    @param names_to_index: converts function ids to an index for unicode sequencing.
    """
    start_unicode_index = 65
    unicode_string = ''
    for node in sequence:
        unicode_string += chr(names_to_index[node])

    # return the unicode string
    return unicode_string



def CreateFuzzyNodeSequenceMapping(dataset):
    """
    Create a mapping between node sequences in this dataset to a unique ID. This
    enables the sequences to collapse to a single node in a graph. The sequences
    need to be an exact match.
    @params dataset: the dataset for which to analyze node sequences
    """
    # start statistics
    start_time = time.time()

    # currently only works if each node can become a character
    names_to_index = GetUniqueNames(dataset)
    assert (len(names_to_index) < 1024)
    # how many names are there and start the mapping at that index
    nnames = len(names_to_index)

    # create the directories for the mappings
    if not os.path.exists('mappings'):
        os.mkdir('mappings')
    if not os.path.exists('mappings/{}'.format(dataset)):
        os.mkdir('mappings/{}'.format(dataset))

    # read all of the traces independent of request type
    traces = dataIO.ReadTraces(dataset, None, None)

    # create a set of all the unique sequences
    sequences = set()

    # go through every trace in the dataset
    for trace in traces:
        # go through every sequence in the dataset
        for sequence in trace.sequences:
            sequences.add(sequence.SequenceTuple())

    # sort the list
    sequences = sorted(list(sequences))
    nsequences = len(sequences)

    # create a union find data structure
    union_find = [UnionFindElement(iv + nnames) for iv in range(nsequences)]

    # go through all pairs of sequences
    for is1 in range(nsequences):
        # get this sequence and convert to a unicode string
        sequence_one = sequences[is1]
        unicode_one = ConvertSequenceToUnicode(sequence_one, names_to_index)

        for is2 in range(is1 + 1, nsequences):
            # get this sequence and convert to a unicode string
            sequence_two = sequences[is2]
            unicode_two = ConvertSequenceToUnicode(sequence_two, names_to_index)

            #  get the difference between these two sequences
            distance = difflib.SequenceMatcher(None, unicode_one, unicode_two).ratio()

            # with enough similarity merge these two sequences
            if distance > 0.925: Union(union_find[is1], union_find[is2])

    # save the sequence to an output filename
    output_filename = 'mappings/{}/fuzzy-node-sequence-to-index.txt'.format(dataset)
    with open(output_filename, 'w') as fd:
        nsequences = len(sequences)
        fd.write('{}\n'.format(nsequences))
        for iv, sequence in enumerate(sequences):
            sequence_length = len(sequence)
            fd.write('{}\n'.format(sequence_length))
            for node in sequence:
                fd.write('{}\n'.format(node))
            fd.write('{}\n'.format(Find(union_find[iv]).label))

    # print statistics
    print ('Created fuzzy sequence name mappings for {} in {:0.2f} seconds.'.format(dataset, time.time() - start_time))
