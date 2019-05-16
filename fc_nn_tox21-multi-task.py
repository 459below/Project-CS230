""" Fully connected Neural Network fingerprints classifier for tox21 """
import os

import tensorflow as tf
import keras
import numpy as np

import matplotlib
matplotlib.use("TkAgg")
from matplotlib import pyplot as plt

from utils.build_dataset import get_data
from utils.misc import set_up_logging, f1_score
from sklearn.metrics import fbeta_score


# Set up logging
LOGGER = set_up_logging(__name__)

def each_metric(input_data, y_test, model):

    classes = np.array(['NR-AR', 'NR-ER-LBD', 'SR-ATAD5'])

    y_pred = model.predict(input_data)

    # Performing masking
    y_pred = (y_pred > 0.5) * 1.0

    total = y_pred.shape[0]

    #each accuracy
    for i in range(y_pred.shape[1]):
        right = 0
        for j in range (total):
            if y_pred[j][i] == y_test[j][i]:
                right+=1
        accuracy = right/total
        print(classes[i], "accuracy:", accuracy)

    print('\n#######################################')
    # each f1 score
    for i in range(y_pred.shape[1]):
        y_p = y_pred[:,i]
        y_t = y_test[:,i]
        f1 = fbeta_score(y_t, y_p, beta=1)
        print(classes[i], "f1 score:", f1)

    return

def fcnn_classifier_tox21(n_x, n_y):
    """
    This function returns a Fully Connected NN keras classifier

    :param n_x:     size of the input
    :param n_y:     size of the output
    :return:        keras untrained Fully Connected NN multi-class classifier
    """
    classifier = keras.Sequential([
        keras.layers.InputLayer(input_shape=(n_x,)),
        keras.layers.Dense(n_x, activation=tf.nn.relu),
        keras.layers.Dense(n_y, activation=tf.nn.sigmoid)
    ])

    classifier.compile(optimizer=tf.train.AdamOptimizer(),
                       loss='binary_crossentropy',
                       metrics=['accuracy', f1_score])

    return classifier


def main(train=False):
    """ Main function """
    # Get train and test dataset
    (x_train, y_train), (x_test, y_test) = get_data('data/tox21_10k_data_all_fingerprints.npz')

    n_x = x_train[0].shape[0]
    n_y = y_train[0].shape[0]


    # Build classifier
    fcnn_clf = fcnn_classifier_tox21(n_x, n_y)

    epochs = 50

    if train:
        # Train classifier
        print('\ntrain the classifier')

        history = fcnn_clf.fit(x_train, y_train, epochs=epochs, validation_split=0.1)

        # Save weights
        fcnn_clf.save_weights('weights/fcnn_tox21_%s_three_full_1layer.h5' % epochs)


        #Get data from history
        print(history.history.keys())
        plt.plot(history.history['acc'])
        plt.plot(history.history['val_acc'])
        plt.title("model accuracy")
        plt.ylabel('accuracy')
        plt.xlabel('epoch')
        plt.xticks(range(0, epochs, 1))
        plt.legend(['train', 'val'], loc='upper left')
        plt.savefig("output/fcnn_tox21_acc_%s_three_full_1layer.png" % epochs)
        plt.show()
        #Save the plot

        #Get data from history
        print(history.history.keys())
        plt.plot(history.history['f1_score'])
        plt.plot(history.history['val_f1_score'])
        plt.title("model F1 score")
        plt.ylabel('F1 score')
        plt.xlabel('epoch')
        plt.xticks(range(0, epochs, 1))
        plt.legend(['train', 'val'], loc='upper left')
        plt.savefig("output/fcnn_tox21_f1_%s_three_full_1layer.png" % epochs)
        plt.show()
        #Save the plot

        #Plot the loss
        plt.plot(history.history['loss'])
        plt.plot(history.history['val_loss'])
        plt.title('model loss')
        plt.ylabel('loss')
        plt.xlabel('epoch')
        plt.xticks(range(0, epochs, 1))
        plt.legend(['train', 'val'], loc='upper left')
        plt.savefig("output/fcnn_tox21_loss_%s_three_full_1layer.png" % epochs)
        plt.show()
    else:
        # Load the model weights
        weights_file_path = os.path.abspath(os.path.join(os.curdir, 'weights/fcnn_tox21_%s.h5' % epochs))
        if not os.path.exists(weights_file_path):
            raise Exception(
                "The weights file path specified does not exists: %s"
                % os.path.exists(weights_file_path)
            )
        fcnn_clf.load_weights(weights_file_path)

    print('\ntest the classifier')
    test_loss, test_acc, test_f1_score = fcnn_clf.evaluate(x_test, y_test)

    print('\n#######################################')
    print('Test loss:', test_loss)
    print('Test accuracy:', test_acc)
    print('Test F1 score:', test_f1_score)
    print('\n#######################################')
    each_metric(x_test, y_test, fcnn_clf)

if __name__ == '__main__':
    main(train=True)

