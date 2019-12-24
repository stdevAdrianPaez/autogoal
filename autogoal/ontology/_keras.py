# coding: utf8

import inspect
import itertools

import keras.layers


def _get_keras_layers(ignore=set(["Lambda", "Layer", "Highway", "MaxoutDense", "Input"])):
    """Load all `keras.layers` classes that inherit from `Layer`, except those in `ignore`."""

    for layer_name in dir(keras.layers):
        if layer_name in ignore:
            continue
        if layer_name[0].isupper():
            layer_clss = getattr(keras.layers, layer_name)
            try:
                if issubclass(layer_clss, keras.layers.Layer):
                    yield layer_clss
            except:
                pass


def _get_keras_layer_args(layer):
    """Computes the mandatory args for the constructor of `layer`, which
    are either `int` or `float`.

    Returns a dictionary mapping arg name to its type.
    """

    init_args = inspect.signature(layer.__init__).parameters
    layers_args = {}

    for arg_name, arg in init_args.items():
        if arg_name in ["self", "args", "kwargs"]:
            continue

        if arg.default == arg.empty:
            layers_args[arg_name] = None

    if not layers_args:
        return {}

    input_sample = keras.layers.Input(shape=(1,))

    for p in itertools.combinations_with_replacement([1.33, 1], len(layers_args)):
        for i, key in enumerate(layers_args):
            layers_args[key] = p[i]

        try:
            layer(**layers_args)(input_sample)
            return {k: v.__class__ for k, v in layers_args.items()}
        except:
            pass

    return None


def build_ontology_keras(onto):
    for layer in _get_keras_layers():
        args = _get_keras_layer_args(layer)

        if args is None:
            continue

        print(layer.__name__)
        layer_instance = onto.NeuralNetworkLayer(layer.__name__ + 'Layer')

        for arg, typ in args.items():
            if typ == int:
                parameter = onto.DiscreteHyperParameter(layer.__name__ + '__' + arg)
                parameter.hasMinIntValue = 0
                parameter.hasMaxIntValue = 100
            elif typ == float:
                parameter = onto.ContinuousHyperParameter(layer.__name__ + '__' + arg)
                parameter.hasMinFloatValue = 0.0
                parameter.hasMaxFloatValue = 100.0

            print(" -", arg, ":", typ.__name__)
            layer_instance.hasParameter.append(parameter)
