import random



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
    first_order_counts = {}
    second_order_counts = {}
    third_order_counts = {}

    # train the Markov model
    for trace in training_traces:
        # go through all of the nodes
        for node in trace.nodes:
            # get the parent of this node
            parent_node = node.parent_node
            # get the grandparent of this node
            if not parent_node == None:
                grandparent_node = parent_node.parent_node
            else:
                grandparent_node = None
            # get the great-grandparent of this node
            if not grandparent_node == None:
                greatgrandparent_node = grandparent_node.parent_node
            else:
                greatgrandparent_node = None

            node_action = '{} {}'.format(node.tracepoint_id, node.variant)

            # add to the dictionary for first order chains
            if parent_node == None: continue
            parent_action = '{} {}'.format(parent_node.tracepoint_id, parent_node.variant)
            if not parent_action in first_order_counts:
                first_order_counts[parent_action] = {}
            if not node_action in first_order_counts[parent_action]:
                first_order_counts[parent_action][node_action] = 1
            else:
                first_order_counts[parent_action][node_action] += 1

            # add to the dictionary for second order chains
            if grandparent_node == None: continue
            grandparent_action = '{} {}'.format(grandparent_node.tracepoint_id, grandparent_node.variant)
            if not (grandparent_action, parent_action) in second_order_counts:
                second_order_counts[(grandparent_action, parent_action)] = {}
            if not node_action in second_order_counts[(grandparent_action, parent_action)]:
                second_order_counts[(grandparent_action, parent_action)][node_action] = 1
            else:
                second_order_counts[(grandparent_action, parent_action)][node_action] += 1

            # add to the dictionary for third order chains
            if greatgrandparent_node == None: continue
            greatgrandparent_action = '{} {}'.format(greatgrandparent_node.tracepoint_id, greatgrandparent_node.variant)
            if not (greatgrandparent_action, grandparent_action, parent_action) in third_order_counts:
                third_order_counts[(greatgrandparent_action, grandparent_action, parent_action)] = {}
            if not node_action in third_order_counts[(greatgrandparent_action, grandparent_action, parent_action)]:
                third_order_counts[(greatgrandparent_action, grandparent_action, parent_action)][node_action] = 1
            else:
                third_order_counts[(greatgrandparent_action, grandparent_action, parent_action)][node_action] += 1

    first_order_transitions = GenerateTransitionMatrix(first_order_counts)
    second_order_transitions = GenerateTransitionMatrix(second_order_counts)
    third_order_transitions = GenerateTransitionMatrix(third_order_counts)

    return first_order_transitions, second_order_transitions, third_order_transitions



def TestMarkovChain(traces, first_order_transitions, second_order_transitions, third_order_transitions, dataset, print_verbose=False):
    # keep track of correctly predicted transitions
    nincomplete_information = 0
    nfirst_order_correct = 0
    nfirst_order_incorrect = 0
    nsecond_order_correct = 0
    nsecond_order_incorrect = 0
    nthird_order_correct = 0
    nthird_order_incorrect = 0

    # go through each testing trace
    for trace in traces:
        # # keep statistics for each trace as well
        # ncorrect_transitions = 0
        # nincorrect_transitions = 0
        # nincomplete_information = 0

        # go through all of the nodes
        for node in trace.nodes:
            # get the parent of this node
            parent_node = node.parent_node
            # don't worry about things that start a chain
            if parent_node == None: continue

            ground_truth_action = '{} {}'.format(node.tracepoint_id, node.variant)

            parent_key = '{} {}'.format(parent_node.tracepoint_id, parent_node.variant)

            if not parent_key in first_order_transitions:
                nincomplete_information += 1
                continue

            action_selection = random.random()

            # get the results for the first order approximation
            for (probability, action) in first_order_transitions[parent_key]:
                if probability < action_selection:
                    break

            first_order_success = (action == ground_truth_action)

            # get the grandparent of this node
            grandparent_node = parent_node.parent_node
            if grandparent_node == None:
                second_order_success = first_order_success
            else:
                grandparent_key = '{} {}'.format(grandparent_node.tracepoint_id, grandparent_node.variant)
                if not (grandparent_key, parent_key) in second_order_transitions:
                    second_order_success == first_order_success
                else:
                    action_selection = random.random()

                    # get the results for the second order approximation
                    for (probability, action) in second_order_transitions[(grandparent_key, parent_key)]:
                        if probability < action_selection:
                            break

                    second_order_success = (action == ground_truth_action)

            # get the great grandparent of this node
            if grandparent_node == None:
                third_order_success = second_order_success
            else:
                greatgrandparent_node = grandparent_node.parent_node
                if greatgrandparent_node == None:
                    third_order_success = second_order_success
                else:
                    greatgrandparent_key = '{} {}'.format(greatgrandparent_node.tracepoint_id, greatgrandparent_node.variant)
                    if not (greatgrandparent_key, grandparent_key, parent_key) in third_order_transitions:
                        third_order_success = first_order_success
                    else:
                        action_selection = random.random()

                        # get the results for the third order approximation
                        for (probability, action) in third_order_transitions[(greatgrandparent_key, grandparent_key, parent_key)]:
                            if probability < action_selection:
                                break

                        third_order_success = (action == ground_truth_action)

            if first_order_success: nfirst_order_correct += 1
            else: nfirst_order_incorrect += 1

            if second_order_success: nsecond_order_correct += 1
            else: nsecond_order_incorrect += 1

            if third_order_success: nthird_order_correct += 1
            else: nthird_order_incorrect += 1

    # print statistics
    print ('First Order Markov Chain {}'.format(dataset))
    print ('  Correct: {}'.format(nfirst_order_correct))
    print ('  Incorrect: {}'.format(nfirst_order_incorrect))
    print ('  Incomplete: {}'.format(nincomplete_information))
    print ('  Accuracy: {:0.2f}%'.format(100 * nfirst_order_correct / (nfirst_order_correct + nfirst_order_incorrect + nincomplete_information)))
    print ()

    # print statistics
    print ('Second Order Markov Chain {}'.format(dataset))
    print ('  Correct: {}'.format(nsecond_order_correct))
    print ('  Incorrect: {}'.format(nsecond_order_incorrect))
    print ('  Incomplete: {}'.format(nincomplete_information))
    print ('  Accuracy: {:0.2f}%'.format(100 * nsecond_order_correct / (nsecond_order_correct + nsecond_order_incorrect + nincomplete_information)))
    print ()

    # print statistics
    print ('Third Order Markov Chain {}'.format(dataset))
    print ('  Correct: {}'.format(nthird_order_correct))
    print ('  Incorrect: {}'.format(nthird_order_incorrect))
    print ('  Incomplete: {}'.format(nincomplete_information))
    print ('  Accuracy: {:0.2f}%'.format(100 * nthird_order_correct / (nthird_order_correct + nthird_order_incorrect + nincomplete_information)))
    print ()
