
import unittest


from pyflo.geometry.vertical import Profile


class VerticalCurveTest(unittest.TestCase):

    def setUp(self):
        self.profile = Profile()
        self.profile.create_pt(113600.00, 063.003)
        self.profile.create_pt(114712.97, 051.873, 0800.0)
        self.profile.create_pt(117454.76, 099.854, 2360.0)
        self.profile.create_pt(119104.00, 052.026, 0800.0)
        self.profile.create_pt(120633.36, 059.673, 0800.0)
        self.profile.create_pt(122474.50, 114.907, 1700.0)
        self.profile.create_pt(124750.00, 108.081, 0800.0)
        self.profile.create_pt(126341.51, 139.911, 2000.0)
        self.profile.create_pt(127829.35, 113.130, 0800.0)
        self.profile.create_pt(131083.05, 103.369, 0800.0)
        self.profile.create_pt(132155.02, 108.729, 1000.0)
        self.profile.create_pt(134842.88, 092.601, 0800.0)
        self.profile.create_pt(136497.65, 112.176)
        self.pt1 = self.profile.pts[1]
        self.pt_next = self.profile.next_pvt_pt(120400.00)

    def test_g1(self):
        expected = -0.010
        produced = self.pt1.g1()
        self.assertAlmostEqual(expected, produced, 3)

    def test_g2(self):
        expected = 0.017
        produced = self.pt1.g2()
        self.assertAlmostEqual(expected, produced, 3)

    def test_r(self):
        expected = 0.344
        produced = self.pt1.r()
        self.assertAlmostEqual(expected, produced, 3)

    def test_pvc_station(self):
        expected = 114312.97
        produced = self.pt1.pvc_station
        self.assertAlmostEqual(expected, produced, 2)

    def test_pvt_station(self):
        expected = 115112.97
        produced = self.pt1.pvt_station
        self.assertAlmostEqual(expected, produced, 2)

    def test_g1_next(self):
        expected = 0.005
        produced = self.pt_next.g1()
        self.assertAlmostEqual(expected, produced, 3)

    def test_r_next(self):
        expected = 0.312
        produced = self.pt_next.r()
        self.assertAlmostEqual(expected, produced, 3)

    def test_pvc_station_next(self):
        expected = 120233.36
        produced = self.pt_next.pvc_station
        self.assertAlmostEqual(expected, produced, 2)

    def test_slopes(self):
        s1 = round(self.profile.slope(120500.00), 3)
        s2 = round(self.profile.slope(120400.00), 3)
        s3 = round(self.profile.slope(120300.00), 3)
        s4 = round(self.profile.slope(120233.36), 3)
        s5 = round(self.profile.slope(119504.00), 3)
        s6 = round(self.profile.slope(119386.35), 3)
        s7 = round(self.profile.slope(119225.00), 3)
        s8 = round(self.profile.slope(119386.35), 3)
        s9 = round(self.profile.slope(119225.00), 3)
        s10 = round(self.profile.slope(119386.35), 3)
        s11 = round(self.profile.slope(120300.00), 3)
        s12 = round(self.profile.slope(120233.36), 3)
        s13 = round(self.profile.slope(119504.00), 3)
        s14 = round(self.profile.slope(119386.35), 3)
        s15 = round(self.profile.slope(117595.00), 3)
        s16 = round(self.profile.slope(117850.00), 3)
        s17 = round(self.profile.slope(118170.00), 3)
        s18 = round(self.profile.slope(118470.00), 3)
        s19 = round(self.profile.slope(118605.00), 3)
        s20 = round(self.profile.slope(118940.00), 3)
        s21 = round(self.profile.slope(119225.00), 3)
        s22 = round(self.profile.slope(119386.35), 3)
        s23 = round(self.profile.slope(114980.00), 3)
        s24 = round(self.profile.slope(114773.06), 3)
        s25 = round(self.profile.slope(114065.00), 3)
        s26 = round(self.profile.slope(114200.00), 3)
        s27 = round(self.profile.slope(114412.85), 3)
        s28 = round(self.profile.slope(114603.88), 3)
        produced = (
            s1, s2, s3, s4, s5, s6, s7, s8, s9, s10, s11, s12, s13, s14, s15, s16, s17, s18, s19, s20,
            s21, s22, s23, s24, s25, s26, s27, s28
        )
        expected = (
            0.013,
            0.010,
            0.007,
            0.005,
            0.005,
            0.000,
            -0.007,
            0.000,
            -0.007,
            0.000,
            0.007,
            0.005,
            0.005,
            0.000,
            -0.009,
            -0.014,
            -0.020,
            -0.026,
            -0.028,
            -0.019,
            -0.007,
            0.000,
            0.013,
            0.006,
            -0.010,
            -0.010,
            -0.007,
            0.000,
        )
        self.assertTupleEqual(expected, produced)

    def test_elevation(self):
        produced = round(self.profile.elevation(114065.00), 3)
        expected = 58.353
        self.assertAlmostEqual(expected, produced, 3)
    
    def test_elevations(self):
        z1 = round(self.profile.elevation(120500.00), 3)
        z2 = round(self.profile.elevation(120400.00), 3)
        z3 = round(self.profile.elevation(120300.00), 3)
        z4 = round(self.profile.elevation(120233.36), 3)
        z5 = round(self.profile.elevation(119504.00), 3)
        z6 = round(self.profile.elevation(119386.35), 3)
        z7 = round(self.profile.elevation(119225.00), 3)
        z8 = round(self.profile.elevation(119386.35), 3)
        z9 = round(self.profile.elevation(120300.00), 3)
        z10 = round(self.profile.elevation(120233.36), 3)
        z11 = round(self.profile.elevation(119504.00), 3)
        z12 = round(self.profile.elevation(119386.35), 3)
        produced = (
            z1, z2, z3, z4, z5, z6, z7, z8, z9, z10, z11, z12
        )
        expected = (
            60.117,
            58.940,
            58.076,
            57.673,
            54.026,
            53.732,
            54.285,
            53.732,
            58.076,
            57.673,
            54.026,
            53.732
        )
        self.assertTupleEqual(expected, produced)

    def test_key_stations(self):
        elevations = [
            113600.00,
            136497.65,
        ]
        pvcs = [
            113600.00,
            114312.97,
            116274.76,
            118704.00,
            120233.36,
            121624.50,
            124350.00,
            125341.51,
            127429.35,
            130683.05,
            131655.02,
            134442.88,
            136497.65,
        ]
        pvts = [
            113600.00,
            115112.97,
            118634.76,
            119504.00,
            121033.36,
            123324.50,
            125150.00,
            127341.51,
            128229.35,
            131483.05,
            132655.02,
            135242.88,
            136497.65,
        ]
        extremums = [
            114603.89,
            117162.93,
            119386.35,
            120073.35,
            123169.96,
            124454.34,
            126394.14,
            128389.35,
            130983.04,
            132109.56,
            134712.11,
        ]
        stations = elevations + pvcs + pvts + extremums
        expected = sorted(list(set(stations)))
        produced = self.profile.key_stations(2)
        self.assertListEqual(produced, expected)

class UnsmoothTest(unittest.TestCase):

    def setUp(self):
        self.profile = Profile()
        self.profile.create_pt(000.0, 2.0)
        self.profile.create_pt(100.0, 0.5)
        self.profile.create_pt(200.0, 0.0)
        self.profile.create_pt(300.0, 1.0)
        self.profile.create_pt(400.0, 1.5)

    def test_negative_unsmooth(self):
        produced = self.profile.slope(100.0)
        expected = self.profile.slope(050.0)
        self.assertEqual(expected, produced)

    def test_positive_unsmooth(self):
        produced = self.profile.slope(300.0)
        expected = self.profile.slope(350.0)
        self.assertEqual(expected, produced)


class KeyStationTest(unittest.TestCase):

    def setUp(self):
        self.profile = Profile()
        self.profile.create_pt(000.0, 1.0)
        self.profile.create_pt(100.0, 2.0, 100.0)
        self.profile.create_pt(200.0, 1.0)

    def test_key_stations(self):
        produced = self.profile.key_stations(2, 33.3333)
        expected = [0.0, 50.0, 83.33, 100.0, 116.67, 150.0, 200.0]
        self.assertListEqual(produced, expected)
