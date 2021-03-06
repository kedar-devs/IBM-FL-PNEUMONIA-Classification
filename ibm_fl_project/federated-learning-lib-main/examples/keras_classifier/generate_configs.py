import os
#i added tf
import tensorflow as tf
#import tensorflow_addons as tfa

import keras
from keras import backend as K
from keras.layers import Conv2D, MaxPooling2D
from keras.layers import Dense, Dropout, Flatten
from keras.models import Sequential

import examples.datahandlers as datahandlers


def get_fusion_config():
    fusion = {
        'name': 'IterAvgFusionHandler',
        'path': 'ibmfl.aggregator.fusion.iter_avg_fusion_handler'
    }
    return fusion


def get_local_training_config():
    local_training_handler = {
        'name': 'LocalTrainingHandler',
        'path': 'ibmfl.party.training.local_training_handler'
    }
    return local_training_handler


def get_hyperparams():
    hyperparams = {
        'global': {
            'rounds': 1,
            'termination_accuracy': 0.9,
            'max_timeout': 6000
        },
        'local': {
            'training': {
                'epochs': 30
            },
            'optimizer': {
                'lr': 0.001
            }
        }
    }

    return hyperparams


def get_data_handler_config(party_id, dataset, folder_data, is_agg=False):

    SUPPORTED_DATASETS = ['mnist']
    if dataset in SUPPORTED_DATASETS:
        data = datahandlers.get_datahandler_config(
            dataset, folder_data, party_id, is_agg)
    else:
        raise Exception(
            "The dataset {} is a wrong combination for fusion/model".format(dataset))
    return data


def get_model_config(folder_configs, dataset, is_agg=False, party_id=0):
    if is_agg:
        return None
 ##############
    num_classes = 1  ## changed
    img_rows, img_cols = 64,64 ## changed
    if K.image_data_format() == 'channels_first':
        input_shape = ( 1,img_rows, img_cols)
    else:
        input_shape = (img_rows, img_cols,1)

    model = Sequential()
    #1st layer
    model.add(Conv2D(32, kernel_size=(3, 3),
                     activation='relu',
                     input_shape=input_shape))
    model.add(MaxPooling2D(pool_size=(2, 2))) # added
    #2nd layer
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(Dropout(0.1))#added
    model.add(MaxPooling2D(pool_size=(2, 2)))
    #3rd layer
    model.add(Conv2D(64, (3, 3), activation='relu'))
    model.add(MaxPooling2D(pool_size=(2, 2)))
    #4th layer  
    model.add(Conv2D(128 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
    model.add(Dropout(0.2))
    model.add(MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
    #5th layer
    model.add(Conv2D(256 , (3,3) , strides = 1 , padding = 'same' , activation = 'relu'))
    model.add(Dropout(0.2))
    model.add(MaxPooling2D((2,2) , strides = 2 , padding = 'same'))
    #Fc layer
    model.add(Flatten())
    model.add(Dense(units = 128 , activation = 'relu'))
    model.add(Dropout(0.2))
    model.add(Dense(units = 1 , activation = 'sigmoid'))
 
    model.compile(loss='binary_crossentropy',
                  optimizer='adam',
                  metrics=['accuracy',tf.keras.metrics.Precision(),tf.keras.metrics.Recall()])  
    model.summary()
    
    if not os.path.exists(folder_configs):
        os.makedirs(folder_configs)

    # Save model
    fname = os.path.join(folder_configs, 'compiled_keras.h5')
    model.save(fname)

    K.clear_session()
    # Generate model spec:
    spec = {
        'model_name': 'keras-cnn',
        'model_definition': fname
    }

    model = {
        'name': 'KerasFLModel',
        'path': 'ibmfl.model.keras_fl_model',
        'spec': spec
    }

    return model
