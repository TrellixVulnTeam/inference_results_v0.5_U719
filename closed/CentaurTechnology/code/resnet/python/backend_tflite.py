"""
tflite backend (https://github.com/tensorflow/tensorflow/lite)
"""

# pylint: disable=unused-argument,missing-docstring,useless-super-delegation

from threading import Lock

import tensorflow as tf
from tensorflow.lite.python import interpreter as interpreter_wrapper

import backend


class BackendTflite(backend.Backend):
    def __init__(self):
        super(BackendTflite, self).__init__()
        self.sess = None
        self.lock = Lock()

        self.sample_count = 0 # Debug

    def version(self):
        return tf.__version__ + "/" + tf.__git_version__

    def name(self):
        return "tflite"

    def image_format(self):
        # tflite is always NHWC
        return "NHWC"

    def load(self, model_path, inputs=None, outputs=None):
        self.sess = interpreter_wrapper.Interpreter(model_path=model_path)
        self.sess.allocate_tensors()
        # keep input/output name to index mapping
        self.input2index = {i["name"]: i["index"] for i in self.sess.get_input_details()}
        self.output2index = {i["name"]: i["index"] for i in self.sess.get_output_details()}
        # keep input/output names
        self.inputs = list(self.input2index.keys())
        self.outputs = list(self.output2index.keys())
        return self

    def predict(self, feed):
        print('sample_count = ' + str(self.sample_count))
        self.sample_count = self.sample_count + 1

        self.lock.acquire()
        # set inputs
        for k, v in self.input2index.items():
            self.sess.set_tensor(v, feed[k])
        self.sess.invoke()
        # get results
        res = [self.sess.get_tensor(v) for _, v in self.output2index.items()]

        self.lock.release()
        return res
