

import unittest
from pyflo import sections


class IrregularSectionTest(unittest.TestCase):
    """
    From https://www.researchgate.net/post/How_can_get_the_wetted_perimeter_in_an_irregular_stream_bank

    """

    def test_problem(self):
        # Calculate the cross sectional area given
        points = [
            (000.0, 00.0),
            (005.0, -2.1),
            (010.0, -3.4),
            (015.0, -5.6),
            (020.0, -4.7),
            (025.0, -3.5),
            (030.0, -4.4),
            (035.0, -5.4),
            (040.0, -6.1),
            (045.0, -5.8),
            (050.0, -5.7),
            (055.0, -5.1),
            (060.0, -6.0),
            (065.0, -6.5),
            (070.0, -7.2),
            (075.0, -7.2),
            (080.0, -8.2),
            (085.0, -5.5),
            (090.0, -3.6),
            (095.0, -3.2),
            (100.0, 00.0)
        ]
        s = sections.Irregular(points)
        produced = s.flow_area(8.2)
        expected = 496
        self.assertAlmostEqual(produced, expected, 1)

    # def test_problem_2(self):
    #     # Calculate the cross sectional area given
    #     points = [
    #         (00.0, 00.0),
    #         (05.0, -91.0),
    #         (10.0, -19.0),
    #         (15.0, -96.0),
    #         (20.0, -76.0),
    #         (25.0, -71.0),
    #         (30.0, -70.0),
    #         (35.0, -81.0),
    #         (40.0, -24.0),
    #         (45.0, -4.0),
    #         (50.0, -41.0),
    #         (55.0, -43.0),
    #         (60.0, -15.0),
    #         (65.0, -10.0),
    #         (70.0, -78.0),
    #         (75.0, -48.0),
    #         (80.0, -51.0),
    #         (85.0, -12.0),
    #         (90.0, -68.0),
    #         (95.0, -72.0),
    #         (100.0, 00.0),
    #     ]
    #     s = sections.Irregular(points)
    #     produced = s.flow_area(8.2)
    #     expected = 4993.33
    #     self.assertAlmostEqual(produced, expected, 2)
