import unittest
from pyflo import sections


class IrregularSectionTest(unittest.TestCase):
    """
    From https://www.researchgate.net/post/How_can_get_the_wetted_perimeter_in_an_irregular_stream_bank
    """

    def test_problem(self):
        # Calculate the cross sectional area given
        points = [(0, 0), (5, -2.1), (10, -3.4), (15, -5.6),
                  (20, -4.7), (25, -3.5), (30, -4.4), (35, -5.4),
                  (40, -6.1), (45, -5.8), (50, -5.7), (55, -5.1),
                  (60, -6), (65, -6.5), (70, -7.2), (75, -7.2),
                  (80, -8.2), (85, -5.5), (90, -3.6), (95, -3.2), (100, 0)]
        s = sections.Irregular(points)
        produced = s.flow_area(8.2)
        expected = 496
        self.assertAlmostEqual(produced, expected, 1)
