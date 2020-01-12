import numpy as np
from tensorflow import keras


def is_numpy(obj):
    """
    Check of the type is instance of numpy array
    :param obj: object to check
    :return: True if the object is numpy-type array.
    """
    return isinstance(obj, (np.ndarray, np.generic))


def ensure_numpy_type(obj):
    """
    Raise exception if it's not a numpy
    :param obj: object to check
    :return: numpy object
    """
    if is_numpy(obj):
        return obj
    else:
        raise AttributeError('Not a numpy type.')


def ensure_tf_type(obj, fake_input_layer=None, name=None):
    """
    Convert to Keras Constant if needed
    :param obj: numpy / tf type
    :param fake_input_layer: fake input layer to add constant
    :return: tf type
    """
    if is_numpy(obj):
        if obj.dtype == np.int64:
            obj = np.int32(obj)

        def target_layer(_, inp=obj, dtype=obj.dtype.name):
            import numpy as np
            import tensorflow as tf
            if not isinstance(inp, (np.ndarray, np.generic)):
                inp = np.array(inp, dtype=dtype)
            return tf.constant(inp, dtype=inp.dtype)

        lambda_layer = keras.layers.Lambda(target_layer, name=name)
        return lambda_layer(fake_input_layer)
    else:
        return obj


def check_torch_keras_error(model, k_model, input_np, epsilon=1e-5, change_ordering=False):
    """
    Check difference between Torch and Keras models
    :param model: torch model
    :param k_model: keras model
    :param input_np: input data
    :param epsilon: allowed difference
    :param change_ordering: change ordering for keras input
    :return: actual difference
    """
    from torch.autograd import Variable
    import torch

    input_var = Variable(torch.FloatTensor(input_np))
    pytorch_output = model(input_var).data.numpy()
    if change_ordering:
        keras_output = k_model.predict(np.transpose(input_np, [0, 2, 3, 1]))
    else:
        keras_output = k_model.predict(input_np)

    error = np.max(pytorch_output - keras_output)

    assert (error < epsilon), "error is {}".format(error)
    return error
