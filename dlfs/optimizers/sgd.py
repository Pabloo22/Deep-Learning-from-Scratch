import numpy as np
from typing import Tuple

from dlfs.optimizers import Optimizer
from dlfs.layers import Layer


class SGD(Optimizer):
    """
    Mini-batch stochastic gradient descent.
    """

    def __init__(self, learning_rate: float = 0.01):
        super(SGD, self).__init__(learning_rate=learning_rate)

    def update(self, layer: Layer, gradients: Tuple[np.ndarray, np.ndarray]):
        """Updates parameters using SGD

        Args:
            layer: The layer to update.
            gradients: delta of parameters (weights and bias)
        """
        dw, db = gradients

        layer.weights -= self.learning_rate * dw
        layer.bias -= self.learning_rate * db

    def add_slot(self, layer: Layer):
        """
        Add a slot for the layer.
        """
        pass
