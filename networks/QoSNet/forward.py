import math



import numpy as np



from keras.models import model_from_json



from network_motifs.utilities import dataIO
from network_motifs.utilities.constants import human_readable, request_types_per_dataset
from network_motifs.networks.QoSNet.features import ReadFeatures
from network_motifs.visualization import network_results



def CalculateResults(model, features, labels, statistics, parameters, subset):
    # create method to visualize results
    nbins = 20
    binned_duration_errors = [0.0 for iv in range(nbins)]
    binned_correct_qos_detection = [0 for iv in range(nbins)]
    binned_occurrences = [0 for iv in range(nbins)]

    nexamples = len(features)
    predictions = model.predict(np.array(features))

    mae = 0.0
    mae_baseline = 0.0
    mae_duration = 0.0

    TP, TN, FP, FN = 0, 0, 0, 0
    for iv in range(nexamples):
        prediction = predictions[iv][0] / 10
        label = labels[iv] / 10

        mae += abs(prediction - label)

        # where in the matrix is this prediction
        if prediction > 1 and label > 1: TP += 1
        elif prediction > 1 and label < 1: FP += 1
        elif prediction < 1 and label > 1: FN += 1
        elif prediction < 1 and label < 1: TN += 1
        else: assert (False)

        # actual duration of this process
        average_duration = statistics[iv][0]
        stddev_duration = statistics[iv][1]
        nnodes = statistics[iv][2]
        actual_duration = label * stddev_duration + average_duration
        predicted_duration = prediction * stddev_duration + average_duration
        mae_duration += abs(predicted_duration - actual_duration)
        mae_baseline += abs(average_duration - actual_duration)

        # how close to the end is this node
        bin = int(math.floor(features[iv][2] / nnodes * nbins))
        binned_duration_errors[bin] += abs(predicted_duration - actual_duration)
        if (prediction > 1 and label > 1) or (prediction < 1 and label < 1):
            binned_correct_qos_detection[bin] += 1
        binned_occurrences[bin] += 1

    mae /= nexamples
    mae_duration /= nexamples
    mae_baseline /= nexamples

    print (subset)
    print ('  Mean Absolute Error (ZScore): {:0.2f}'.format(mae))
    if (mae_duration > 10**9):
        print ('  Mean Absolute Error (Duration): {:0.2f} seconds'.format(mae_duration / 10**9))
    else:
        print ('  Mean Absolute Error (Duration): {:0.2f}'.format(mae_duration))
    if (mae_baseline > 10**9):
        print ('  Mean Absolute Error (Baseline): {:0.2f} seconds'.format(mae_baseline / 10**9))
    else:
        print ('  Mean Absolute Error (Baseline): {:0.2f}'.format(mae_baseline))
    print ('  True Positives: {}'.format(TP))
    print ('  False Positives: {}'.format(FP))
    print ('  False Negatives: {}'.format(FN))
    print ('  True Negatives: {}'.format(TN))
    print ('  Baseline: {:0.2f}'.format(100 * (TN + FP) / (TP + FP + FN + TN)))
    print ('  Accuracy: {:0.2f}'.format(100 * (TP + TN) / (TP + FP + FN + TN)))

    # update the results for each bin based on number of occurrences
    for bin in range(nbins):
        if binned_occurrences[bin]:
            binned_duration_errors[bin] /= binned_occurrences[bin]
            binned_correct_qos_detection[bin] /= binned_occurrences[bin]
            binned_correct_qos_detection[bin] *= 100.0


    return binned_correct_qos_detection, binned_duration_errors, binned_occurrences


def Forward(dataset):
    for request_type in request_types_per_dataset[dataset]:
        # read the training and validation features from disk
        #training_filenames = dataIO.ReadTrainingFilenames(dataset, request_type)
        #validation_filenames = dataIO.ReadValidationFilenames(dataset, request_type)
        testing_filenames = dataIO.ReadTestingFilenames(dataset, request_type)

        #training_features, training_labels, training_statistics = ReadFeatures(dataset, training_filenames)
        #validation_features, validation_labels, validation_statistics = ReadFeatures(dataset, validation_filenames)
        testing_features, testing_labels, testing_statistics = ReadFeatures(dataset, testing_filenames)

        parameters = {}
        parameters['first-layer'] = 512
        parameters['second-layer'] = 256
        parameters['third-layer'] = 128
        parameters['batch_size'] = 1000
        parameters['nfeatures'] = testing_features[0].size

        # get the prefix for where this model is saved
        if request_type == None:
            model_prefix = 'networks/QoSNet/architectures/{}-params-{}-{}-{}-batch-size-{}'.format(dataset, parameters['first-layer'], parameters['second-layer'], parameters['third-layer'], parameters['batch_size'])
        else:
            model_prefix = 'networks/QoSNet/architectures/{}-request-type-{}-params-{}-{}-{}-batch-size-{}'.format(dataset, request_type, parameters['first-layer'], parameters['second-layer'], parameters['third-layer'], parameters['batch_size'])

        # load the model with best weights
        model = model_from_json(open('{}.json'.format(model_prefix), 'r').read())
        model.load_weights('{}-best-loss.h5'.format(model_prefix))

        if request_type == None:
            print (human_readable[dataset])
        else:
            print ('{} {}'.format(human_readable[dataset], request_type))
        #CalculateResults(model, training_features, training_labels, training_statistics, parameters, 'Training')
        #CalculateResults(model, validation_features, validation_labels, validation_statistics, parameters, 'Validation')
        accuracies, duration_errors, occurrences = CalculateResults(model, testing_features, testing_labels, testing_statistics, parameters, 'Testing')

        output_filename_prefix = '{}-results'.format(model_prefix)
        if request_type == None:
            title = '{}'.format(human_readable[dataset])
        else:
            title = '{} {}'.format(human_readable[dataset], request_type)

        network_results.VisualizeNetworkDurations(output_filename_prefix, title, accuracies, duration_errors, occurrences)
