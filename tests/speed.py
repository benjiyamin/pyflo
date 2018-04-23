
import time
import unittest


class SpeedTest(unittest.TestCase):

    def setUp(self):
        self.startTime = time.time()
        self.test_data = [i for i in range(100)]

    def tearDown(self):
        t = time.time() - self.startTime
        print("%s: %.6fs" % ('speed', t))

    def test_list_comprehension(self):
        x_new = [i for i in range(1000)]

    def test_generator_expression(self):
        x_new = (i for i in range(1000))

    def test_generator_expression_and_list(self):
        x_new = (i for i in range(1000))
        y_new = list(x_new)

    # def test_generator(self):
    #     for pair in iterators.gen_pair(self.test_data):
    #         pass
