def GenerateFeatures(dataset, training_traces, testing_traces):
    # go through every node in every trace
    # for training data, get statistics for the total trace
    for training_trace in training_traces:
        duration = training_trace.duration
        nnodes = len(training_trace.nodes)

    for testing_trace in testing_traces:
        pass
