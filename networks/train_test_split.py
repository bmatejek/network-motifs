import os
import random



def SplitTraces(dataset, traces):
    # do not allow any more splits
    # currently we assume all functions occur in trainval and testing
    assert (False)

    # there are three different request_types for this set of traces
    traces_by_request_types = {}
    for request_type in request_types:
        traces_by_request_types[request_type] = []

    for trace in traces:
        if not trace.request_type in traces_by_request_types:
            traces_by_request_types[trace.request_type] = []
        traces_by_request_types[trace.request_type].append(trace)

    training_filenames = []
    validation_filenames = []
    testing_filenames = []

    # create the list of training and testing files
    for request_type in traces_by_request_types:
        traces = traces_by_request_types[request_type]
        random.shuffle(traces)

        train_split = len(traces) // 2
        validation_split = (len(traces) * 3) // 4

        training_traces = traces[:train_split]
        validation_traces = traces[train_split:validation_split]
        testing_traces = traces[validation_split:]

        with open('traces/{}/{}-training-traces.txt'.format(dataset, request_type), 'w') as fd:
            for trace in training_traces:
                trace_filename = 'traces/{}/{}.trace'.format(dataset, trace.base_id)
                assert (os.path.exists(trace_filename))
                training_filenames.append(trace_filename)
                fd.write('{}\n'.format(trace_filename))

        with open('traces/{}/{}-validation-traces.txt'.format(dataset, request_type), 'w') as fd:
            for trace in validation_traces:
                trace_filename = 'traces/{}/{}.trace'.format(dataset, trace.base_id)
                assert (os.path.exists(trace_filename))
                validation_filenames.append(trace_filename)
                fd.write('{}\n'.format(trace_filename))

        with open('traces/{}/{}-testing-traces.txt'.format(dataset, request_type), 'w') as fd:
            for trace in testing_traces:
                trace_filename = 'traces/{}/{}.trace'.format(dataset, trace.base_id)
                assert (os.path.exists(trace_filename))
                testing_filenames.append(trace_filename)
                fd.write('{}\n'.format(trace_filename))

    # make sure the three lists are disjoint
    assert (set(training_filenames).isdisjoint(set(testing_filenames)))
    assert (set(training_filenames).isdisjoint(set(validation_filenames)))
    assert (set(validation_filenames).isdisjoint(set(testing_filenames)))
