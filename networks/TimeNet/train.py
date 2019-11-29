import random


import numpy as np



from keras.models import Sequential
from keras.layers import Dense, Activation



from network_motifs.data_structures.trace import GetUniqueRequestTypes




def TimeNet(parameters):
	# create simple model for this neural network
    model = Sequential()
    model.add(Dense(4, input_dim=2))
    model.add(Activation('relu'))
    model.add(Dense(2))
    model.add(Activation('relu'))
    model.add(Dense(1))

    # compile the model
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['accuracy'])

    return model


def GenerateExamples(traces, parameters):
    batch_size = parameters['batch_size']

    data = np.zeros((batch_size, 2), dtype=np.int64)
    labels = np.zeros((batch_size), dtype=np.int64)

    request_types = sorted(GetUniqueRequestTypes(traces))
    request_type_to_int = {}
    for iv, request_type in enumerate(request_types):
        request_type_to_int[request_type] = iv

    while True:
        for iv in range(batch_size):
            # randomly choose one of the traces
            trace = random.choice(traces)
            node = random.choice(trace.ordered_nodes[5:-5])

            avg_nodes = 0
            counts = 0
            avg_time = 0
            for train_trace in traces:
                if train_trace.request_type == trace.request_type:
                    avg_nodes += len(trace.nodes)
                    avg_time += trace.maximum_timestamp
                    counts += 1
            avg_nodes /= counts
            avg_time /= counts

            #data[iv,0] = request_type_to_int[trace.request_type]
            #data[iv,1] = node.index
            data[iv,0] = node.timestamp
            #data[iv,3] = avg_nodes
            data[iv,1] = avg_time

            # the amount of time before the request finishes
            labels[iv] = trace.maximum_timestamp - node.timestamp

        yield (data, labels)


def TrainValidationSplit(traces):
    # split the data into training and validation datasets
    request_types = GetUniqueRequestTypes(traces)
    traces_per_request = {}
    for request_type in request_types:
        traces_per_request[request_type] = []
    # split up the traces by request
    for trace in traces:
        traces_per_request[trace.request_type].append(trace)

    # get training/validation split
    trainval_split = 0.8
    training_traces = []
    validation_traces = []
    for request_type in request_types:
        ntraces = len(traces_per_request[request_type])
        split_index = int(round(trainval_split * ntraces))

        # add the traces to the training and validation sets
        training_traces += traces_per_request[request_type][:split_index]
        validation_traces += traces_per_request[request_type][split_index:]

    return training_traces, validation_traces



def Train(dataset, traces):
    # transform the trainval traces into training and validation sets
    training_traces, validation_traces = TrainValidationSplit(traces)

    parameters = {}
    parameters['batch_size'] = 10

    # read the simple model
    model = TimeNet({})

    examples_per_epoch = 20000
    batch_size = parameters['batch_size']

    model.fit_generator(
                        GenerateExamples(training_traces, parameters),
                        steps_per_epoch=examples_per_epoch // batch_size,
                        epochs=500,
                        validation_data=GenerateExamples(validation_traces, parameters),
                        validation_steps=examples_per_epoch // batch_size,
                        )
