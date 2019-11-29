import random



def ToOrdinal(value):
    """
    Convert a numerical value into an ordinal number.
    @param value: the number to be converted
    """

    if value % 100//10 != 1:
        if value % 10 == 1:
            ordval = '{}st'.format(value)
        elif value % 10 == 2:
            ordval = '{}nd'.format(value)
        elif value % 10 == 3:
            ordval = '{}rd'.format(value)
        else:
            ordval = '{}th'.format(value)
    else:
        ordval = '{}th'.format(value)

    return ordval



def GenerateTransitionMatrix(counts):
    """
    Convert a countr matrix into a probability transition matrix.
    @param counts: for each key, how many times is the future node seen
    """

    transitions = {}

    for key in counts:
        destination_actions = counts[key]

        # initialize the empty list
        transitions[key] = []

        # how many times was this key seen
        noccurrences = 0

        for action in destination_actions:
            noccurrences += destination_actions[action]

        # keep track of cumulative probabilities
        cumulative_probability = 0.0
        for action in destination_actions:
            cumulative_probability += destination_actions[action] / noccurrences
            transitions[key].append((cumulative_probability, action))

    return transitions



def TrainMarkovChain(training_traces, max_order, k = 1):
    """
    Create Markov Chain model from the training traces.
    @param training_traces: list of traces for model generation
    @param max_order: the maximum number of nodes to look at in the past
    @param k: the number of nodes in the future to predict
    """

    # parameter verification
    assert (len(training_traces))
    assert (max_order > 0)
    assert (k > 0)

    # next estimates are aggregated over all training_traces
    counts = {}

    # train the Markov model
    for trace in training_traces:
        # go through every node in the trace in timestamp order
        nnodes = len(trace.nodes)
        for iv in range(nnodes):
            # what node in the future are we trying to predict
            future_node = trace.KthNode(iv + k)
            if future_node == None: continue
            future_node = future_node.Name()

            key = ()
            # go through all orders sequentially
            for io in range(max_order):
                ancestor_node = trace.KthNode(iv - io)
                if ancestor_node == None: continue

                key = (ancestor_node.Name(),) + key

                # has this key been seen before?
                if not key in counts:
                    counts[key] = {}
                # has  this future node been seen before?
                if not future_node in counts[key]:
                    counts[key][future_node] = 1
                else:
                    counts[key][future_node] += 1

    # convert the counts from above to transitions from a given key
    transitions = GenerateTransitionMatrix(counts)

    return transitions



def TestMarkovChain(traces, transitions, max_order, k = 1, print_verbose = False):
    """
    Predict future nodes based on max_order previous nodes.
    @param traces: list of traces for prediction
    @param transitions: set of transition probabilities from training iteration
    @param max_order: the maximum number of nodes to look at in the past
    @param k: the number of nodes in the future to predict
    @param: print_verbose: print out the results for each node
    """

    # create counts for the correct/incorrect for each order markov chain
    ncorrect_transitions = [0 for _ in range(max_order)]
    nincorrect_transitions = [0 for _ in range(max_order)]
    nincomplete_information = [0 for _ in range(max_order)]

    # make sure all the keys are less than the order size
    for key in transitions:
        assert (len(key) <= max_order)

    # go through each testing trace
    for trace in traces:
        # go through every node in the trace in timestamp order
        nnodes = len(trace.nodes)
        for iv in range(nnodes):
            # what node in the future are we trying to predict
            future_node = trace.KthNode(iv + k)
            if future_node == None: continue
            future_node = future_node.Name()

            # what was the result from the previous order
            previous_result = 2

            key = ()
            # go through all orders sequentially
            for io in range(max_order):
                ancestor_node = trace.KthNode(iv - io)
                # can no longer use
                if not ancestor_node == None:
                    key = (ancestor_node.Name(),) + key

                if not key in transitions:
                    if previous_result == 0: nincorrect_transitions[io] += 1
                    elif previous_result == 1: ncorrect_transitions[io] += 1
                    elif previous_result == 2: nincomplete_information[io] += 1
                    else: assert(False)
                    continue

                rand_function = random.random()
                for (probability, function) in transitions[key]:
                    if (rand_function < probability):
                        break

                if function == future_node:
                    ncorrect_transitions[io] += 1
                    previous_result = 1
                else:
                    nincorrect_transitions[io] += 1
                    previous_result = 0

    # calculate the accuracy for each order
    accuracies = []

    for iv in range(max_order):
        accuracy = 100 * ncorrect_transitions[iv] / (ncorrect_transitions[iv] + nincorrect_transitions[iv] + nincomplete_information[iv])

        if print_verbose:
            print ('{} Order Markov Chain for k = {}'.format(ToOrdinal(iv + 1), k))
            print ('  Correct: {}'.format(ncorrect_transitions[iv]))
            print ('  Incorrect: {}'.format(nincorrect_transitions[iv]))
            print ('  Incomplete: {}'.format(nincomplete_information[iv]))
            print ('  Accuracy: {:0.2f}%'.format(accuracy))
            print ()

        accuracies.append(accuracy)

    return accuracies
