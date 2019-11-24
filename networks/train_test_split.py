import os
import random



def SplitOpenStackTraces(open_stack_traces):
    # there are three different request_types for this set of traces
    traces_by_request_types = {}
    traces_by_request_types['ServerDelete'] = []
    traces_by_request_types['ServerCreate'] = []
    traces_by_request_types['ServerList'] = []

    for trace in open_stack_traces:
        traces_by_request_types[trace.request_type].append(trace)

    training_filenames = []
    testing_filenames = []

    # create the list of training and testing files
    for request_type in traces_by_request_types:
        traces = traces_by_request_types[request_type]
        random.shuffle(traces)

        split_index = len(traces) // 2

        training_traces = traces[:split_index]
        testing_traces = traces[split_index:]

        for trace in training_traces:
            trace_filename = 'openstack-json/{}.json'.format(trace.base_id)
            assert (os.path.exists(trace_filename))
            training_filenames.append(trace_filename)

        for trace in testing_traces:
            trace_filename = 'openstack-json/{}.json'.format(trace.base_id)
            assert (os.path.exists(trace_filename))
            testing_filenames.append(trace_filename)

    # make sure the two lists are disjoint
    assert (set(training_filenames).isdisjoint(set(testing_filenames)))

    # write the two files
    training_list_filename = 'openstack-json/training-open-stack-traces.txt'
    with open(training_list_filename, 'w') as fd:
        for training_filename in training_filenames:
            fd.write('{}\n'.format(training_filename))

    testing_list_filename = 'openstack-json/testing-open-stack-traces.txt'
    with open(testing_list_filename, 'w') as fd:
        for testing_filename in testing_filenames:
            fd.write('{}\n'.format(testing_filename))
