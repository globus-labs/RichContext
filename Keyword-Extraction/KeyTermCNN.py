from keras.models import Sequential, load_model
from keras.layers import Dense, Dropout, Activation, Flatten, Convolution1D, MaxPooling1D
from keras.utils import np_utils, plot_model
from keras import backend as K

import numpy as np
import sys
import os

K.set_image_data_format('channels_first')

'''
A wrapper class to streamline the creation, saving, and loading of a Keras 1 dimension convolutional
neural network. The models that are saved can be used with or without the wrapper class.
'''
class CNN_1D(object):

    '''
    Creates a 1d convolutional neural network model that can either apply single or multiple labels
    Input parameters are further described in the Keras documentation.
    '''
    def __init__(self, multi_label=True, input_dim=(1000, 100), output_dim=100,
                drop_1 = .2, drop_2 = .5, num_filters=64, filter_frame=3,
                stride=1, pool_size=2):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.multi_label = multi_label
        self.model = Sequential()
        self.model.add(Convolution1D(num_filters, filter_frame,
                activation='relu', input_shape=input_dim))
        self.model.add(Convolution1D(num_filters, filter_frame, activation='relu'))
        self.model.add(MaxPooling1D(pool_size=pool_size))
        self.model.add(Dropout(drop_1))
        self.model.add(Flatten())
        self.model.add(Dense(2*output_dim, activation='relu'))
        self.model.add(Dropout(drop_2))
        if multi_label == True:
            self.model.add(Dense(output_dim, activation='sigmoid'))
        else:
            self.model.add(Dense(output_dim, activation='softmax'))
        self.model.compile(loss='binary_crossentropy',
            optimizer='rmsprop', metrics=['accuracy'])
        return
    '''
    loads a 1d CNN from a specified path given input and output dimension. File to load must
    be .h5 file.
    '''
    def from_file(self, filepath, multi_label=True, input_dim=(1000, 100), output_dim=100):
        self.input_dim = input_dim
        self.output_dim = output_dim
        self.model = load_model(filepath)
        self.multi_label = multi_label
    '''
    Basic application of the Keras .train(...) method, refer to the Keras documentation for this.
    '''
    def train(self, x_train, y_train, batch_size=32, nb_epochs=5, verbose=1):
        self.model.fit(x_train, y_train, batch_size=batch_size, 
            nb_epoch=nb_epochs, verbose=verbose)
        return

    '''
    See Keras documentation
    '''
    def predict(self, x_test, verbose=1):
        predictions = self.model.predict(x_test, verbose=verbose)
        return predictions

    '''
    See Keras documentation
    '''
    def score(self, x_test, y_test, verbose=1):
        score = self.model.evaluate(x_test, y_test, verbose=verbose)
        return score
    '''
    See Keras documentation
    '''
    def save(self, filepath):
        self.model.save(filepath)
        return

