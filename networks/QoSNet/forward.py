import os
import math
import struct



import numpy as np



from keras.models import model_from_json



from network_motifs.utilities import dataIO
from network_motifs.utilities.constants import human_readable, request_types_per_dataset
from network_motifs.networks.QoSNet.features import ReadFeatures
from network_motifs.visualization.network_results import VisualizeNetworkDurations



def CalculateResults(dataset, request_type, model, features, labels, parameters, nnodes):
    # read in critical statistics
    statistics_filename = 'statistics/QoS-{}-{}.stat'.format(dataset, request_type)
    with open(statistics_filename, 'rb') as fd:
        avg_duration, stddev_duration, qos_threshold, = struct.unpack('fff', fd.read(12))

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

    correct = 0

    TP, TN, FP, FN = 0, 0, 0, 0
    for iv in range(nexamples):
        prediction = predictions[iv][0] / 10
        label = labels[iv] / 10

        mae += abs(prediction - label)
        # actual duration of this process
        actual_duration = label * stddev_duration + avg_duration
        predicted_duration = prediction * stddev_duration + avg_duration
        mae_duration += abs(predicted_duration - actual_duration)
        mae_baseline += abs(avg_duration - actual_duration)
        qos_ground_truth = actual_duration > qos_threshold
        qos_prediction = predicted_duration > qos_threshold
        if qos_ground_truth == qos_prediction: correct += 1

        # where in the matrix is this prediction
        if qos_prediction and qos_ground_truth: TP += 1
        elif qos_prediction and not qos_ground_truth: FP += 1
        elif not qos_prediction and qos_ground_truth: FN += 1
        elif not qos_prediction and not qos_ground_truth: TN += 1
        else: assert (False)

        # how close to the end is this node
        bin = int(math.floor(features[iv][2] / nnodes[iv] * nbins))
        binned_duration_errors[bin] += abs(predicted_duration - actual_duration)
        if (prediction > 1 and label > 1) or (prediction < 1 and label < 1):
            binned_correct_qos_detection[bin] += 1
        binned_occurrences[bin] += 1

    mae /= nexamples
    mae_duration /= nexamples
    mae_baseline /= nexamples

    print ('{} {}'.format(dataset, request_type))

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
    #print ('  Baseline: {:0.2f}'.format(100 * (TN + FP) / (TP + FP + FN + TN)))
    #print ('  Accuracy: {:0.2f}'.format(100 * (TP + TN) / (TP + FP + FN + TN)))
    print ('  Accuracy: {:0.2f}'.format(correct / nexamples))

    # update the results for each bin based on number of occurrences
    for bin in range(nbins):
        if binned_occurrences[bin]:
            binned_duration_errors[bin] /= binned_occurrences[bin]
            binned_correct_qos_detection[bin] /= binned_occurrences[bin]
            binned_correct_qos_detection[bin] *= 100.0

    return binned_correct_qos_detection, binned_duration_errors, binned_occurrences


def Forward(dataset):
    # create a new model for every request type
    for request_type in request_types_per_dataset[dataset]:
        testing_filenames = dataIO.ReadTestingFilenames(dataset, request_type)

        testing_features, testing_labels, nnodes = ReadFeatures(dataset, testing_filenames)

        parameters = {}
        parameters['first-layer'] = 512
        parameters['second-layer'] = 256
        parameters['third-layer'] = 128
        parameters['batch_size'] = 1000
        parameters['nfeatures'] = testing_features[0].size

        # get the prefix for where this model is saved
        model_prefix = 'networks/QoSNet/architectures/{}-request-type-{}-params-{}-{}-{}-batch-size-{}'.format(dataset, request_type, parameters['first-layer'], parameters['second-layer'], parameters['third-layer'], parameters['batch_size'])

        # load the model with best weights
        model = model_from_json(open('{}.json'.format(model_prefix), 'r').read())
        model.load_weights('{}-best-loss.h5'.format(model_prefix))

        accuracies, duration_errors, occurrences = CalculateResults(dataset, request_type, model, testing_features, testing_labels, parameters, nnodes)

        output_filename_prefix = '{}-results'.format(model_prefix)
        title = '{} {}'.format(human_readable[dataset], request_type)

        VisualizeNetworkDurations(output_filename_prefix, title, accuracies, duration_errors, occurrences)
