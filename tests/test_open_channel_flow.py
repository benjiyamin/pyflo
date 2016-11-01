
import unittest

from pyflo import links, sections


class RectangularChannelsTest(unittest.TestCase):
    """From Practice Problems for the Civil Engineering PE Exam by Michael R. Lindeburg, PE:
    Chapter 19

    """

    def test_practice_problem_1(self):
        s = sections.Rectangle(span=2.0, rise=9999.0, n=0.012)
        flume = links.Reach(invert_1=1.0, invert_2=0.0, length=100.0, section=s)
        flow = 3.0
        produced = flume.normal_depth(flow)
        expected = 0.314
        self.assertAlmostEqual(produced, expected, 3)

    def test_practice_problem_2(self):
        pass

    def test_practice_problem_3(self):
        pass


class CircularChannelsTest(unittest.TestCase):
    """From Practice Problems for the Civil Engineering PE Exam by Michael R. Lindeburg, PE:
    Chapter 19

    """

    def test_practice_problem_4a(self):
        pass

    def test_practice_problem_4b(self):
        pass

    def test_practice_problem_4c(self):
        pass

    def test_practice_problem_4d(self):
        pass
