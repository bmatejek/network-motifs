from keras.models import Sequential
from keras.layers import Activation, Convolution1D, Dense, Flatten, MaxPooling1D
from keras.layers.advanced_activations import LeakyReLU
from keras.optimizers import SGD



from network_motifs.utilities import dataIO
from network_motifs.networks.RequestNet import generate_features



def RequestNetModel(input_size):
    model = Sequential()
    print (input_size)
    model.add(Convolution1D(32, (5,), padding='same', input_shape=input_size))
    model.add(LeakyReLU(alpha=0.01))
    model.add(Convolution1D(32, (5,), padding='same'))
    model.add(LeakyReLU(alpha=0.01))
    model.add(MaxPooling1D(pool_size=2))
    model.add(Flatten())
    model.add(Dense(512))
    model.add(LeakyReLU(alpha=0.01))
    model.add(Dense(32))
    model.add(Activation('sigmoid'))
    model.add(Dense(3))
    model.add(Activation('sigmoid'))
    
    opt = SGD(lr=0.001, decay=5e-8, momentum=0.99, nesterov=True)
    model.compile(loss='mean_squared_error', optimizer=opt, metrics=['accuracy'])

    return model



def Generator(dataset, base_ids, input_size, batch_size):
    # get the list of words for this dataset
    words, outputs = generate_features.FeatureWords(dataset)
    nwords = len(words)

    node_list = {}
    
    # read in the features for this dataset
    for base_id in base_ids:
        feature_filename = 'request-net/{}-features/{}.features'.format(dataset, base_id)

        nodes = []
        
        with open(feature_filename, 'r') as fd:
            label = fd.readline().strip()

            # add in all of the features for this node
            for line in fd.readlines():
                nodes.append(line)

        # create a list for all labels
        if not label in node_list:
            node_list[label] = []
            
        node_list[label].append(nodes)

    for iv in range(batch_size):
        request_type = outputs[iv]

        nodes = node_list[request_type]

        start = randint(0, len(nodes) - 1)
        #seq = 
    
            

def Train(dataset, input_size):
    # read the training and testing filenames
    training_traces_filename = '{}-json/training-{}-traces.txt'.format(dataset, dataset)
    with open(training_traces_filename, 'r') as fd:
        trainval_base_ids = []
        for filename in fd.read().splitlines():
            base_id = filename.split('/')[1].split('.')[0]
            trainval_base_ids.append(base_id)
            
    # split into training and validation datasets
    trainval_split = 0.8
    split_index = int(round(len(trainval_base_ids) * trainval_split))
    
    train_base_ids = trainval_base_ids[:split_index]
    validation_base_ids = trainval_base_ids[split_index:]

    batch_size = 3
    
    # get the model for this network
    model = RequestNetModel((batch_size, input_size))

    model.fit_generator(Generator(dataset, train_base_ids, input_size, batch_size),
                        validation_data=Generator(dataset, validation_base_ids, input_size, batch_size))
