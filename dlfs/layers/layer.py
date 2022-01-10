from abc import ABC, abstractmethod
import numpy as np
from typing import Optional

from dlfs.activation_functions import ActivationFunction, get_activation_function


class Layer(ABC):
    """
    Base class for all layers.

    Args:
        input_shape (tuple or None): Shape of the input.
        output_shape (tuple): Shape of the output.
        activation (str): Activation function to use.
        name (str): Name of the layer.
        trainable (bool): Whether the layer is trainable.
    """

    def __init__(self,
                 input_shape: Optional[tuple] = None,
                 output_shape: Optional[tuple] = None,
                 activation: Optional[str] = None,
                 name: str = None,
                 trainable: bool = True,
                 has_weights: bool = True):

        self.input_shape = input_shape if input_shape else None
        self.output_shape = output_shape
        self.name = name
        self.weights = None
        self.bias = None
        self.__has_weights = has_weights  # Whether the layer has weights and biases.
        self.trainable = trainable
        self.initialized = False
        self.__activation = get_activation_function(activation)
        self.inputs = None
        self.z = None  # output of the layer before activation

    # Getters
    # -------------------------------------------------------------------------

    @property
    def activation(self) -> ActivationFunction:
        return self.__activation

    @property
    def has_weights(self) -> bool:
        return self.__has_weights

    # Setters
    # -------------------------------------------------------------------------

    @activation.setter
    def activation(self, activation: str):
        self.__activation = get_activation_function(activation)

    # Abstract methods
    # -------------------------------------------------------------------------

    @abstractmethod
    def initialize(self, input_shape: tuple):
        raise NotImplementedError

    @abstractmethod
    def forward(self, inputs: np.ndarray, training: bool = False) -> np.ndarray:
        """
        Forward pass of the layer.
        Args:
            inputs: input to the layer.
            training: whether the layer is in training mode.
        Returns:
            output of the layer.
        """

    @abstractmethod
    def set_weights(self, weights: np.ndarray = None, bias: np.ndarray = None):
        raise NotImplementedError

    def get_delta(self, d_out: np.ndarray) -> np.ndarray:
        """
        Args:
            d_out: derivative of the cost function with respect to the output of this layer.
        Returns:
            The delta of the layer (d_C/d_z).
        """
        # check if the layer is initialized
        if not self.initialized:
            raise ValueError("The layer is not initialized")

        if self.activation is None:
            delta = d_out
        else:
            activation_gradient = self.activation.gradient(self.z)
            # check if the gradient is a matrix of tensors
            #
            # For example, in the case of Dense layers, we have to check if the gradient is a matrix of tensors
            # with shape=(m, n_neurons) or a tensor of jacobian matrices with shape=(m, n_neurons, n_neurons)
            # This is because of activation functions such
            # as softmax which returns a matrix of jacobian matrices.

            if activation_gradient.shape == self.z.shape:
                delta = d_out * activation_gradient
            else:
                d_out = d_out[:, np.newaxis, :]
                delta = np.einsum('ijk,ikl->il', d_out, activation_gradient)

                # The above einsum is equivalent to:
                # delta = np.empty_like(self.z)
                # batch_size = self.input_shape.shape[0]
                # for i in range(batch_size):  # for each sample
                #     delta[i] = d_out[i] @ activation_gradient[i]

        return delta

    @abstractmethod
    def get_d_inputs(self, delta: np.ndarray) -> np.ndarray:
        """
        Returns the derivative of the cost function with respect to the input of the layer.
        Args:
            delta: derivative of the cost function with respect to the output of the layer.
        Returns:
            derivative of the cost function with respect to the input of the layer.
        """

    @abstractmethod
    def summary(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def update(self, optimizer, gradients: np.ndarray):
        """
        Updates the weights and biases of the layer.
        Args:
            optimizer (Optimizer): optimizer to use.
            gradients: gradients of the cost function with respect to the weights and biases of the layer.
        """
        raise NotImplementedError

    @abstractmethod
    def count_params(self) -> int:
        raise NotImplementedError

    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
