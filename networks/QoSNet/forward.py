from keras.models import model_from_json



from network_motifs.utilities import dataIO
from network_motifs.networks.QoSNet.features import ReadFeatures
from network_motifs.networks.QoSNet.train import GenerateExamples


def CalculateResults(model, features, labels, parameters, subset):
    nexamples = len(features)
    predictions = model.predict_generator(GenerateExamples(features, labels, parameters, subset='testing'), nexamples, max_queue_size=1000)[:nexamples]

    #print (predictions)
    mae = 0
    TP, TN, FP, FN = 0, 0, 0, 0
    for iv in range(nexamples):
        mae += abs(predictions[iv] - labels[iv])[0]

        if predictions[iv] > 1 and labels[iv] > 1: TP += 1
        if predictions[iv] > 1 and labels[iv] < 1: FP += 1
        if predictions[iv] < 1 and labels[iv] > 1: FN += 1
        if predictions[iv] < 1 and labels[iv] < 1: TN += 1
    mae /= nexamples

    print (subset)
    print ('  MAE: {:0.2f}'.format(mae))
    print ('  True Positives: {}'.format(TP))
    print ('  False Positives: {}'.format(FP))
    print ('  False Negatives: {}'.format(FN))
    print ('  True Negatives: {}'.format(TN))
    print ('  Baseline: {:0.2f}'.format(100 * (TN + FP) / (TP + FP + FN + TN)))
    print ('  Accuracy: {:0.2f}'.format(100 * (TP + TN) / (TP + FP + FN + TN)))



def Forward(dataset):
    # read the training and validation features from disk
    training_filenames = dataIO.ReadTrainingFilenames(dataset)
    validation_filenames = dataIO.ReadValidationFilenames(dataset)
    testing_filenames = dataIO.ReadTestingFilenames(dataset)

    training_features, training_labels = ReadFeatures(dataset, training_filenames)
    validation_features, validation_labels = ReadFeatures(dataset, validation_filenames)
    testing_features, testing_labels = ReadFeatures(dataset, testing_filenames)

    parameters = {}
    parameters['first-layer'] = 80
    parameters['second-layer'] = 40
    parameters['batch_size'] = 1000
    parameters['nfeatures'] = training_features[0].size

    # get the prefix for where this model is saved
    model_prefix = 'networks/QoSNet/architectures/{}-params-{}-{}-batch-size-{}'.format(dataset, parameters['first-layer'], parameters['second-layer'], parameters['batch_size'])
    # load the model with best weights
    model = model_from_json(open('{}.json'.format(model_prefix), 'r').read())
    model.load_weights('{}-best-loss.h5'.format(model_prefix))

    CalculateResults(model, training_features, training_labels, parameters, 'Training')
    CalculateResults(model, validation_features, validation_labels, parameters, 'Validation')
    CalculateResults(model, testing_features, testing_labels, parameters, 'Testing')
