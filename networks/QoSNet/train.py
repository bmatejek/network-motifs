import random
import keras



import numpy as np



from keras.models import Sequential
from keras.layers import Dense, Activation, BatchNormalization, Dropout



from network_motifs.utilities import dataIO
from network_motifs.networks.QoSNet.features import ReadFeatures



def QoSNet(parameters):
    # create simple model for this neural network
    model = Sequential()
    model.add(Dense(parameters['first-layer'], input_dim=parameters['nfeatures']))
    model.add(Activation('sigmoid'))
    #model.add(Dropout(0.2))
    model.add(Dense(parameters['second-layer']))
    model.add(Activation('sigmoid'))
    #model.add(Dropout(0.5))
    model.add(Dense(1))

    # compile the model
    model.compile(optimizer='adam', loss='mean_squared_error', metrics=['mse'])

    return model



def GenerateExamples(dataset_features, dataset_labels, parameters, subset='trainval'):
    # get stats about the learning process
    ndata_points = len(dataset_features)
    batch_size = parameters['batch_size']
    nfeatures = parameters['nfeatures']

    input_features = np.zeros((batch_size, nfeatures), dtype=np.float32)
    input_labels = np.zeros(batch_size, dtype=np.int32)

    indices = [iv for iv in range(ndata_points)]
    if subset == 'trainval': random.shuffle(indices)

    # current index in features/labels lists
    index = 0
    while True:
        for iv in range(batch_size):
            features = dataset_features[indices[index]]
            label = dataset_labels[indices[index]]

            # put into format for learning
            input_features[iv,:] = features
            input_labels[iv] = label

            # reset the index if overflow
            index += 1
            if index == len(features):
                index = 0
                if subset == 'trainval': random.shuffle(indices)

        # yield the created features and labels
        if subset == 'trainval': yield (input_features, input_labels)
        else: yield input_features



def Train(dataset):
    # read the training and validation features from disk
    training_filenames = dataIO.ReadTrainingFilenames(dataset)
    validation_filenames = dataIO.ReadValidationFilenames(dataset)

    training_features, training_labels = ReadFeatures(dataset, training_filenames)
    validation_features, validation_labels = ReadFeatures(dataset, validation_filenames)

    parameters = {}
    parameters['first-layer'] = 5
    parameters['second-layer'] = 5
    parameters['batch_size'] = 10
    parameters['nfeatures'] = training_features[0].size

    # create the simple model
    model = QoSNet(parameters)

    # how many example to run for each epoch
    examples_per_epoch = 5000
    batch_size = parameters['batch_size']

    model_prefix = 'networks/QoSNet/architectures/{}-params-{}-{}-batch-size-{}'.format(dataset, parameters['first-layer'], parameters['second-layer'], batch_size)

    # create the set of keras callbacks
    callbacks = []
    best_loss = keras.callbacks.ModelCheckpoint('{}-best-loss.h5'.format(model_prefix), monitor='val_loss', verbose=0, save_best_only=True, save_weights_only=True, mode='auto', period=1)
    callbacks.append(best_loss)

    json_string = model.to_json()
    open('{}.json'.format(model_prefix), 'w').write(json_string)

    model.fit_generator(
                        GenerateExamples(training_features, training_labels, parameters),
                        steps_per_epoch=examples_per_epoch // batch_size,
                        epochs=75,
                        callbacks=callbacks,
                        validation_data=GenerateExamples(validation_features, validation_labels, parameters),
                        validation_steps=examples_per_epoch // batch_size
                        )
