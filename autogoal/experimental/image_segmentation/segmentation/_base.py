from autogoal.utils import nice_repr
from autogoal.kb._algorithm import Supervised
from autogoal.kb import AlgorithmBase, algorithm, Seq
import numpy as np
from ..kb._generated import ImageReader
from ..kb._semantics import ImageFile
from autogoal.kb._semantics import Tensor3
import tensorflow as tf


@nice_repr
class ImageSegmenter(AlgorithmBase):
    """
    Receives images and returns segmentation masks with same size
    """

    def __init__(self, segmenter: algorithm(Seq[Tensor3], Supervised[Seq[Tensor]], Seq[Tensor]),
                 image_preprocessor: algorithm(ImageFile, Tensor3)):
        self._segmenter = segmenter
        self._mode = "train"
        self.image_preprocessor = image_preprocessor

    def train(self):
        self._mode = "train"
        self._segmenter.train()

    def eval(self):
        self._mode = "eval"
        self._segmenter.eval()

    def fit(self, images, masks):
        self._segmenter.fit(self._preprocess_images(images), self._preprocess_masks(masks))

    def _preprocess_images(self, images) -> Seq[Tensor3]:
        p_images = []
        for image in images:
            p_images.append(self.image_preprocessor.run(image))
        return p_images

    def _preprocess_masks(self, images) -> Seq[Tensor]:
        reader = ImageReader()
        p_images = []
        for image_file in images:
            t = reader.run(image_file)
            resize = tf.image.resize(t, [512, 512])
            p_images.append(np.array(resize))
        return p_images

    def predict(self, images):
        return self._segmenter.predict(self._preprocess_images(images))

    def run(self, data: Seq[ImageFile], masks: Supervised[Seq[Tensor]]) -> Seq[Tensor]:
        if self._mode == "train":
            self.fit(data, masks)
            return masks
        if self._mode == "eval":
            return self.predict(data)


@nice_repr
class ImagePreprocessor(AlgorithmBase):
    """
    Receives image file and converts it into appropriate input
    """

    def __init__(self) -> None:
        self.reader = ImageReader()

    def run(self, image_file: ImageFile) -> Tensor3:
        t = self.reader.run(image_file)
        resize = tf.image.resize(t, [512, 512])
        return np.array(resize)
