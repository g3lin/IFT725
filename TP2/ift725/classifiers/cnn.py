# Code adapté de projets académiques de la professeur Fei Fei Li et de ses étudiants Andrej Karpathy, Justin Johnson et autres.
# Version finale rédigée par Carl Lemaire, Vincent Ducharme et Pierre-Marc Jodoin

import numpy as np

from ift725.layers import *
from ift725.quick_layers import *
from ift725.layer_combo import *


class ThreeLayerConvolutionalNet(object):
    """
    A three-layer convolutional network with the following architecture:

    conv - relu - 2x2 max pool - affine - relu - affine - softmax

    The network operates on minibatches of data that have shape (N, C, H, W)
    consisting of N images, each with height H and width W and with C input
    channels.
    """

    def __init__(self, input_dim=(3, 32, 32), num_filters=32, filter_size=7,
                 hidden_dim=100, num_classes=10, weight_scale=1e-2, reg=0.0,
                 dtype=np.float32):
        """
        Initialize a new network.

        Inputs:
        - input_dim: Tuple (C, H, W) giving size of input data
        - num_filters: Number of filters to use in the convolutional layer
        - filter_size: Size of filters to use in the convolutional layer
        - hidden_dim: Number of units to use in the fully-connected hidden layer
        - num_classes: Number of scores to produce from the final affine layer.
        - weight_scale: Scalar giving standard deviation for random initialization
          of weights.
        - reg: Scalar giving L2 regularization strength
        - dtype: numpy datatype to use for computation.
        """
        self.params = {}
        self.reg = reg
        self.dtype = dtype

        ############################################################################
        # TODO: Initialisez les poids et les biais pour le réseau de convolution à #
        #  trois couches.                                                          #
        # Les poids devraient être initialisé à partir d'une Gaussienne avec un    #
        # écart-type égal à weight_scale; les biais devraient être initialisés à 0.#
        # Tous les poids et les biais devraient être emmagasinés dans le           #
        # dictionnaire self.params.                                                #
        # Emmagasinez les poids et les biais de la couche de convolution en        #
        # utilisant les clés 'W1' et 'b1' respectivement; utilisez les clés 'W2'   #
        # et 'b2' pour les poids et les biais de la couche cachée affine et        #
        # utilisez les clés 'W3' et 'b3' pour les poids et les biais de la couche  #
        # affine de sortie.                                                        #
        ############################################################################
        W1dim = (num_filters,input_dim[0],filter_size,filter_size)
        self.params['W1'] = np.random.normal(0, weight_scale, W1dim ).astype(dtype=int)
        self.params['b1'] = np.zeros(num_filters)

        self.params['W2'] = np.random.normal(0, weight_scale, hidden_dim).astype(dtype=int)
        self.params['b2'] = np.zeros(hidden_dim)

        self.params['W3'] = np.random.normal(0, weight_scale,  num_classes).astype(dtype=int)
        self.params['b3'] = np.zeros(num_classes)

        ############################################################################
        #                             FIN DE VOTRE CODE                            #
        ############################################################################

        for k, v in self.params.items():
            self.params[k] = v.astype(dtype)

    def loss(self, X, y=None):
        """
        Evaluate loss and gradient for the three-layer convolutional network.

        Inputs:
        - X: Array of input data of shape (N, C, H, W)
        - y: Array of labels, of shape (N,). y[i] gives the label for X[i].

        Input / output: Same API as TwoLayerNet in fc_net.py.
        """
        W1, b1 = self.params['W1'], self.params['b1']
        W2, b2 = self.params['W2'], self.params['b2']
        W3, b3 = self.params['W3'], self.params['b3']

        # pass conv_param to the forward pass for the convolutional layer
        filter_size = W1.shape[2]
        conv_param = {'stride': 1, 'pad': (filter_size - 1) / 2}

        # pass pool_param to the forward pass for the max-pooling layer
        pool_param = {'pool_height': 2, 'pool_width': 2, 'stride': 2}

        scores = None
        ############################################################################
        # TODO: Implémentez la propagation pour ce réseau de convolution à trois   #
        #  couches, calculant les scores de classes pour X et stockez-les dans la  #
        #  variable scores.                                                        #
        ############################################################################
        # Couche de convolution
        print(self.params['W1'])
        layer_1, cache_layer_1 = forward_convolutional_relu_pool(X, self.params['W1'], self.params['b1'],conv_param,pool_param)
        
        # Couche cachee
        layer_2, cache_layer_2 = forward_fully_connected(layer_1, self.params['W2'], self.params['b2'])
        relu_2, cache_relu_2 = forward_relu(layer_2)

        #Couche de sortie
        layer_3, cache_layer_3 = forward_fully_connected(relu_2, self.params['W3'], self.params['b3'])

        scores = layer_3

        ############################################################################
        #                             FIN DE VOTRE CODE                            #
        ############################################################################

        if y is None:
            return scores

        loss, grads = 0, {}
        ############################################################################
        # TODO: Implémentez la passe arrière pour ce réseau de convolution à trois #
        #  couches, en stockant la perte et les gradients dans les variables loss  #
        #  et grads.                                                               #
        # Calculez la perte de données en utilisant softmax et assurez-vous que    #
        # grads[k] contient les gradients pour self.params[k]. N'oubliez pas       #
        # d'ajouter la régularisation L2!                                          #
        ############################################################################

        # Softmax
        loss, dx = softmax_loss(scores, y)

        # Retro-propagation 3e couche
        dx_layer_3, dw_layer_3, db_layer_3 = backward_fully_connected(dx, cache_layer_3)

        # Retro-propagation 2e couche
        dx_layer_2, dw_layer_2, db_layer_2 = backward_fully_connected(dx, cache_layer_2)
        dx_relu_1 = backward_relu(dx_layer_2, cache_relu_2)


        # Retro-propagation 1ere couche
        dx_layer_1, dw_layer_1, db_layer_1 = backward_convolutional_relu_pool(dx_relu_1, cache_layer_1)

        # Ajouter le terme de regularisation
        grads['W1'] = dw_layer_1 + 0.5 * self.reg * self.params['W1']
        grads['b1'] = db_layer_1 + 0.5 * self.reg * self.params['b1']
        grads['W2'] = dw_layer_2 + 0.5 * self.reg * self.params['W2']
        grads['b2'] = db_layer_2 + 0.5 * self.reg * self.params['b2']
        grads['W2'] = dw_layer_3 + 0.5 * self.reg * self.params['W3']
        grads['b2'] = db_layer_3 + 0.5 * self.reg * self.params['b3']

        loss += self.reg * (np.linalg.norm(self.params['W1'])**2 + np.linalg.norm(self.params['b1'])**2 + np.linalg.norm(self.params['W2'])**2 + np.linalg.norm(self.params['b2'])**2 + np.linalg.norm(self.params['W3'])**2 + np.linalg.norm(self.params['b3'])**2)


        ############################################################################
        #                             FIN DE VOTRE CODE                            #
        ############################################################################

        return loss, grads


pass
