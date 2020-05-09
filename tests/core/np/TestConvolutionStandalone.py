import unittest

from core import info, log_at_info
import numpy as np
import core.np.Nodes as node
import core.np.Convolution as conv
import math
import matplotlib.pyplot as plt
from core import debug
import os
from sklearn.datasets import fetch_openml


class MyTestCase(unittest.TestCase):

    def test_download_mnist(self):
        X, y = fetch_openml('mnist_784', version=1, return_X_y=True)

    def rgb2gray(self, rgb):
        return np.dot(rgb[..., :3], [0.2989, 0.5870, 0.1140])

    def test_convolution_small(self):
        img = np.array([[1, 2, 3, 4], [3, 4, 5, 6], [-1, 0, 1, 3], [0, 2, -1, 4]])
        kernel = np.array([[1, -1], [0, 2]])
        img_node = node.VarNode('img')

        c2d = conv.Convolution2D(img_node, input_shape=(4, 4), kernel=kernel)
        var_map = {'img': img}
        img_node.forward(var_map, None, self)
        info("Original x into the convolution layer")
        info(repr(img))
        output_image = c2d.value(var_map)
        info("Output of the convolution layer")
        expected_output = np.array([[7., 9., 11.],
                                    [-1., 1., 5.],
                                    [3., -3., 6.]])
        np.testing.assert_array_almost_equal(expected_output, output_image)
        info(repr(output_image))
        log_at_info()
        c2d.backward(output_image * 0.1, self, var_map, "")
        info("Kernel before gradient descent")
        info(repr(c2d.get_kernel()))

        def optimizer_function(_w, grad):
            return _w - 0.001 * grad

        optimizer = node.OptimizerIterator([img_node], c2d, optimizer_function)
        loss = optimizer.step(var_map, np.ones_like(output_image))
        info("Printing loss matrix - not really loss  but just the output of the last node")
        info(repr(loss))
        info("Printing kernel after gradient descent")
        info(repr(c2d.get_kernel()))
        expected_kernel = np.array([[0.982, -1.028],
                                    [-0.013, 1.976]])
        info("Print kernel gradient ")
        info(repr(c2d.kernel_grad))
        np.testing.assert_array_almost_equal(expected_kernel, c2d.get_kernel())
        self.assertAlmostEqual(-0.009, c2d.get_bias())
        info("Bias after gradient descent:{}".format(c2d.get_bias()))

    def test_convolution2d_plotting(self):
        image_path = os.path.join('test.data', 'conv2d', 'Vd-Orig.png')
        image = plt.imread(image_path)
        shape = image.shape
        print("shape {}".format(shape))

        img_node = node.VarNode('x')
        x_image = self.rgb2gray(image * 20)
        print(x_image.shape)
        plt.imshow(x_image)
        plt.show()
        debug("Now showing ..")
        var_map = {'x': x_image}
        x_shape = (image.shape[0], image.shape[1])
        conv_node = conv.Convolution2D(img_node, x_shape)
        img_node.forward(var_map, None, self)
        final_image = conv_node.value(var_map)
        plt.imshow(final_image)
        plt.show()
        edge_kernel = np.array([[-1, -1, -1], [-1, 8, -1], [-1, -1, -1]])
        img_node = node.VarNode('x')
        conv_node = conv.Convolution2D(img_node, x_shape, kernel=edge_kernel)
        img_node.forward(var_map, None, self)
        edge_img = conv_node.value(var_map)
        plt.imshow(edge_img)
        plt.show()

    def test_maxpool2d(self):
        pass

    def simple_name(self):
        return self.__class__.__name__


if __name__ == '__main__':
    unittest.main()