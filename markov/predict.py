import random



# variable to control the maximum order of markov chains
max_order = 4


def ToOrdinal(value):
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



def TrainMarkovChain(training_traces):
    # next estimates are aggregated over all training_traces
    counts = {}

    # train the Markov model
    for trace in training_traces:
        # go through all of the nodes
        for node in trace.nodes:
            # skip nodes that are the first envoked
            if node.parent_id == trace.base_id: continue

            # get the action associated with this node
            node_action = '{} {}'.format(node.tracepoint_id, node.variant)

            # continue until the ancestor no longer exists
            ancestor_node = node.parent_node

            key = ()            # keep a record of the keys for each loop iteration
            order = 1           # restrict how many orders are allowed
            while not ancestor_node == None:
                ancestor_action = '{} {}'.format(ancestor_node.tracepoint_id, ancestor_node.variant)
                key = (ancestor_action,) + key

                # add this key to the list of transitions
                if not key in counts:
                    counts[key] = {}
                # add the target to the array of transitions
                if not node_action in counts[key]:
                    counts[key][node_action] = 1
                else:
                    counts[key][node_action] += 1

                # update to the parent of the current ancestor
                ancestor_node = ancestor_node.parent_node

                # sensible restrictions to the maximum value of the chain
                if order == max_order: break
                order += 1

    # convert the counts from above to transitions from a given key
    transitions = GenerateTransitionMatrix(counts)

    return transitions



def TestMarkovChain(traces, transitions, dataset, print_verbose=False):
    # create counts for the correct/incorrect for each order markov chain
    ncorrect_transitions = [0 for _ in range(max_order)]
    nincorrect_transitions = [0 for _ in range(max_order)]
    nincomplete_information = [0 for _ in range(max_order)]

    # go through each testing trace
    for trace in traces:
        # go through all of the nodes
        for node in trace.nodes:
            # skip nodes that are the first envoked
            if node.parent_id == trace.base_id: continue

            # get the action associated with this node
            ground_truth_action = '{} {}'.format(node.tracepoint_id, node.variant)

            # start with the parent of this node
            ancestor_node = node.parent_node

            # keep track of the lower order result
            # 0 is incorrect, 1 is correct, 2 is incomplete
            previous_result = 2

            # continue for all allowable orders
            key = ()
            for order in range(max_order):
                # do not continue down this chain, just use the previous result
                if ancestor_node == None:
                    if previous_result == 0: nincorrect_transitions[order] += 1
                    elif previous_result == 1: ncorrect_transitions[order] += 1
                    elif previous_result == 2: nincomplete_information[order] += 1
                    else: assert (False)

                    # continue to the next order
                    continue

                # get the action for this ancestor
                ancestor_action = '{} {}'.format(ancestor_node.tracepoint_id, ancestor_node.variant)
                key = (ancestor_action,) + key

                # if this nevery happened before, use previous result
                if not key in transitions:
                    if previous_result == 0: nincorrect_transitions[order] += 1
                    elif previous_result == 1: ncorrect_transitions[order] += 1
                    elif previous_result == 2: nincomplete_information[order] += 1
                    else: assert (False)

                    # continue to the next order
                    continue

                selected_action = random.random()

                for (probability, action) in transitions[key]:
                    if probability < selected_action:
                        break

                if action == ground_truth_action:
                    previous_result = 1
                    ncorrect_transitions[order] += 1
                else:
                    previous_result = 0
                    nincorrect_transitions[order] += 1

                # update the ancestor node
                ancestor_node = ancestor_node.parent_node

    for iv in range(max_order):
        order = iv + 1
        print ('{} Order Markov Chain {}'.format(ToOrdinal(order), dataset))
        print ('  Correct: {}'.format(ncorrect_transitions[iv]))
        print ('  Incorrect: {}'.format(nincorrect_transitions[iv]))
        print ('  Incomplete: {}'.format(nincomplete_information[iv]))
        print ('  Accuracy: {:0.2f}%'.format(100 * ncorrect_transitions[iv] / (ncorrect_transitions[iv] + nincorrect_transitions[iv] + nincomplete_information[iv])))
        print ()






    #
    #
    # # print statistics
    # print ('First Order Markov Chain {}'.format(dataset))
    # print ('  Correct: {}'.format(nfirst_order_correct))
    # print ('  Incorrect: {}'.format(nfirst_order_incorrect))
    # print ('  Incomplete: {}'.format(nincomplete_information))
    # print ('  Accuracy: {:0.2f}%'.format(100 * nfirst_order_correct / (nfirst_order_correct + nfirst_order_incorrect + nincomplete_information)))
    # print ()
    #
    # # print statistics
    # print ('Second Order Markov Chain {}'.format(dataset))
    # print ('  Correct: {}'.format(nsecond_order_correct))
    # print ('  Incorrect: {}'.format(nsecond_order_incorrect))
    # print ('  Incomplete: {}'.format(nincomplete_information))
    # print ('  Accuracy: {:0.2f}%'.format(100 * nsecond_order_correct / (nsecond_order_correct + nsecond_order_incorrect + nincomplete_information)))
    # print ()
    #
    # # print statistics
    # print ('Third Order Markov Chain {}'.format(dataset))
    # print ('  Correct: {}'.format(nthird_order_correct))
    # print ('  Incorrect: {}'.format(nthird_order_incorrect))
    # print ('  Incomplete: {}'.format(nincomplete_information))
    # print ('  Accuracy: {:0.2f}%'.format(100 * nthird_order_correct / (nthird_order_correct + nthird_order_incorrect + nincomplete_information)))
    # print ()
