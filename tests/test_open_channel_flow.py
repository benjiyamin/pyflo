
import unittest

from pyflo import links, sections


class RectangularChannelsTest(unittest.TestCase):
    """From Practice Problems for the Civil Engineering PE Exam by Michael R. Lindeburg, PE:
    Chapter 19

    """

    def test_practice_problem_1(self):
        # A wooden flume (n = 0.012) with a rectangular cross section is 2ft wide. The flume carries
        # 3 CFS of water down a 1% slope. What is the depth of flow.
        s = sections.Rectangle(span=2.0, rise=9999.0, n=0.012)
        flume = links.Reach(section=s, slope=0.01)
        flow = 3.0
        produced = flume.normal_depth(flow)
        expected = 0.314  # ft
        self.assertAlmostEqual(produced, expected, 3)


class CircularChannelTest(unittest.TestCase):
    """From Practice Problems for the Civil Engineering PE Exam by Michael R. Lindeburg, PE:
    Chapter 19

    """

    def setUp(self):
        # A 24 in diameter pipe (n = 0.013) was installed 30 years ago on a 0.001 slope. Recent
        # tests indicate that the full-flow capacity of the pipe is 6.0 CFS.
        self.s = sections.Circle(diameter=2.0, n=0.013)
        self.pipe = links.Reach(section=self.s, slope=0.001)

    def test_practice_problem_4a(self):
        # (a) What was the original full-flow capacity?
        produced = self.pipe.normal_flow(depth=self.s.rise)
        expected = 7.2  # CFS
        self.assertAlmostEqual(produced, expected, 1)

    def test_practice_problem_4b(self):
        # (b) What was the original full-flow velocity?
        produced = self.pipe.velocity(depth=self.s.rise)
        expected = 2.3  # ft/s
        self.assertAlmostEqual(produced, expected, 1)


class TrapezoidalChannelTest(unittest.TestCase):
    """From Practice Problems for the Civil Engineering PE Exam by Michael R. Lindeburg, PE:
    Chapter 19

    """

    def test_practice_problem_9(self):
        # The trapezoidal channel shown has a Manning coefficient of n = 0.013 and is laid at a
        # slope of 0.002. The depth of flow is 2 ft. What is the flow rate?
        # [Picture shows 1:3 slopes and 6 ft bottom]
        s = sections.Trapezoid(l_slope=3.0, b_width=6.0, r_slope=3.0, n=0.013)
        channel = links.Reach(section=s, slope=0.002)
        produced = channel.normal_flow(depth=2.0)
        expected = 150.0  # ft/s
        self.assertAlmostEqual(produced, expected, -1)


class FDOTChannelTest(unittest.TestCase):
    """From FDOT Drainage Design Guide Example 3.1-1 - Discharge Given Normal Depth:

    Given:
        Depth = 0.6 ft
        Longitudinal Slope = 0.005 ft/ft
        Trapezoidal Cross Section
            1:4 Left Slope
            5 ft Bottom
            1:6 Right Slope
        Manning’s Roughness = 0.06

    Calculate:
        Discharge, assuming normal depth

    """

    def setUp(self):
        self.depth = 0.6
        self.section = sections.Trapezoid(l_slope=4.0, b_width=5.0, r_slope=6.0, n=0.06)
        self.channel = links.Reach(section=self.section, slope=0.005)

    def test_step_1_1(self):
        # Calculate Wetted Perimeter
        produced = self.section.wet_perimeter(self.depth)
        expected = 11.124  # ft
        self.assertAlmostEqual(produced, expected, 3)

    def test_step_1_2(self):
        # Calculate Cross-Sectional Area
        produced = self.section.flow_area(self.depth)
        expected = 4.8  # ft^2
        self.assertAlmostEqual(produced, expected, 1)

    def test_step_2(self):
        # Calculate Hydraulic Radius
        produced = self.section.hyd_radius(self.depth)
        expected = 0.4315  # ft
        self.assertAlmostEqual(produced, expected, 3)

    def test_step_3(self):
        # Calculate Average Velocity
        produced = self.channel.velocity(self.depth)
        expected = 1.0  # ft/s
        self.assertAlmostEqual(produced, expected, 0)

    def test_step_4(self):
        # Calculate the Discharge
        produced = self.channel.normal_flow(self.depth)
        expected = 4.8  # cfs
        self.assertAlmostEqual(produced, expected, 1)
