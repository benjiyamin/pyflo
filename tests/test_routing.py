
import unittest

from pyflo import networks, system, sections, routing, distributions
from pyflo.nrcs import hydrology


class ReservoirTest(unittest.TestCase):

    def setUp(self):
        contours = [
            (14.0, 0.75 * 43560.0),
            (17.0, 0.81 * 43560.0),
            (17.0, 2.95 * 43560.0),
            (26.0, 4.46 * 43560.0),
            (30.5, 5.10 * 43560.0),
            (01.5, 6.07 * 43560.0),
        ]
        self.reservoir = routing.Reservoir(contours=contours)

    def test_reorder_on_init(self):
        data = self.reservoir.contours
        control = [
            (01.5, 6.07 * 43560.0),
            (14.0, 0.75 * 43560.0),
            (17.0, 0.81 * 43560.0),
            (17.0, 2.95 * 43560.0),
            (26.0, 4.46 * 43560.0),
            (30.5, 5.10 * 43560.0),
        ]
        self.assertListEqual(data, control)

    def test_solve_stage(self):
        control_elevation = 20.0
        storage = self.reservoir.storage(control_elevation)
        elevation = self.reservoir.stage(storage)
        self.assertAlmostEqual(control_elevation, elevation)


class BleedDownTest(unittest.TestCase):

    def setUp(self):
        network = networks.Network()
        nw5 = network.create_node()
        self.contours = [
            (16.0, 0.10 * 43560.0),
            (21.5, 0.42 * 43560.0),
            (23.5, 0.61 * 43560.0),
            (29.8, 1.25 * 43560.0)
        ]
        self.reservoir = routing.Reservoir(contours=self.contours, start_stage=25.35)
        nw5.add_reservoir(reservoir=self.reservoir)
        out = network.create_node()
        diameter = 3.25 / 12.0
        ci3 = sections.Circle(diameter=diameter)
        nw5.create_weir(node_2=out, invert=23.5, k_orif=0.6, k_weir=3.2, section=ci3)
        interval = 5.0 / 60.0
        self.analysis = routing.Analysis(node=out, tw=0.0, duration=2.0, interval=interval)

    def test_storage_stage_below_bottom(self):
        storage = self.reservoir.storage(15.0)
        self.assertEqual(storage, 0.0)

    def test_storage_stage_above_top(self):
        storage = self.reservoir.storage(30.0)
        control = self.reservoir.storage(29.8)
        self.assertGreater(storage, control)

    def test_node_solution_results(self):
        results = self.analysis.node_solution_results()
        data = results[0]['data']
        last_stage = data[-1]['stage']
        control = 25.28
        self.assertAlmostEqual(last_stage, control, 2)


class BasinTest(unittest.TestCase):

    def setUp(self):
        runoff_dist = system.tuple_list_from_csv('./resources/distributions/runoff/scs484.csv')
        self.uh484 = distributions.Distribution(runoff_dist)
        self.basin = hydrology.Basin(
            area=4.6,
            cn=85.0,
            tc=2.3,
            runoff_dist=self.uh484,
            peak_factor=484.0
        )
        self.ratio_pairs = [
            (0.00, 0.000),
            (0.05, 0.074),
            (0.10, 0.174),
            (0.15, 0.280),
            (0.20, 0.378),
            (0.25, 0.448),
            (0.30, 0.496),
            (0.35, 0.526),
            (0.40, 0.540),
            (0.45, 0.540),
            (0.50, 0.540),
            (0.55, 0.542),
            (0.60, 0.554),
            (0.65, 0.582),
            (0.70, 0.640),
            (0.75, 0.724),
            (0.80, 0.816),
            (0.85, 0.886),
            (0.90, 0.940),
            (0.95, 0.980),
            (1.00, 1.000)
        ]

    def test_peak_time(self):
        data = self.basin.peak_time
        control = 1.53
        self.assertAlmostEqual(data, control, 2)

    def test_peak_runoff(self):
        data = self.basin.peak_runoff
        control = 1455.0
        self.assertAlmostEqual(data, control, -1)

    def test_runoff_hydrograph_by_step(self):
        peak_time = 1.53
        peak_runoff = 1455.0
        # self.uh484.plot()
        hydrograph = self.uh484.scaled_by(x=peak_time, y=peak_runoff, x_step=0.1)
        # hydrograph.plot()
        data = hydrograph.data
        data = [(round(line[0], 3), round(line[1], 0)) for line in data]
        control = [
            (0.000, 0.0),
            (0.153, 44.0),
            (0.306, 146.0),
            (0.459, 276.0),
            (0.612, 451.0),
            (0.765, 684.0),
            (0.918, 960.0),
            (1.071, 1193.0),
            (1.224, 1353.0),
            (1.377, 1440.0),
            (1.530, 1455.0),
            (1.683, 1440.0),
            (1.836, 1353.0),
            (1.989, 1251.0),
            (2.142, 1135.0),
            (2.295, 989.0),
            (2.448, 815.0),
            (2.601, 669.0),
            (2.754, 567.0),
            (2.907, 480.0),
            (3.060, 407.0),
            (3.213, 354.0),
            (3.366, 301.0),
            (3.519, 258.0),
            (3.672, 214.0),
            (3.825, 185.0),
            (3.978, 156.0),
            (4.131, 134.0),
            (4.284, 112.0),
            (4.437, 96.0),
            (4.590, 80.0),
            (4.743, 69.0),
            (4.896, 58.0),
            (5.049, 50.0),
            (5.202, 42.0),
            (5.355, 36.0),
            (5.508, 31.0),
            (5.661, 26.0),
            (5.814, 22.0),
            (5.967, 19.0),
            (6.120, 16.0),
            (6.273, 14.0),
            (6.426, 13.0),
            (6.579, 11.0),
            (6.732, 9.0),
            (6.885, 7.0),
            (7.038, 6.0),
            (7.191, 4.0),
            (7.344, 3.0),
            (7.497, 1.0),
            (7.650, 0.0)
        ]
        self.assertListEqual(data, control)

    def test_runoff_hydrograph_by_interval(self):
        peak_time = 1.53
        peak_runoff = 1455.0
        hydrograph = self.uh484.scaled_by(x=peak_time, y=peak_runoff, x_delta=0.3)
        data = hydrograph.data
        data = [(round(line[0], 1), round(line[1], 0)) for line in data]
        control = [
            (0.0, 0.0),
            (0.3, 142.0),
            (0.6, 437.0),
            (0.9, 928.0),
            (1.2, 1328.0),
            (1.5, 1452.0),
            (1.8, 1374.0),
            (2.1, 1167.0),
            (2.4, 870.0),
            (2.7, 603.0),
            (3.0, 436.0),
            (3.3, 324.0),
            (3.6, 234.0),
            (3.9, 171.0),
            (4.2, 124.0),
            (4.5, 89.0),
            (4.8, 65.0),
            (5.1, 48.0),
            (5.4, 35.0),
            (5.7, 25.0),
            (6.0, 18.0),
            (6.3, 14.0),
            (6.6, 11.0),
            (6.9, 7.0),
            (7.2, 4.0),
            (7.5, 1.0),
            (7.8, 0.0)
        ]
        self.assertListEqual(data, control)

    def test_rainfall_hydrograph(self):
        rainfall_dist = distributions.Distribution(self.ratio_pairs)
        hydrograph = rainfall_dist.scaled_by(x=6.0, y=5.0)
        data = hydrograph.data
        data = [(round(line[0], 1), round(line[1], 2)) for line in data]
        control = [
            (0.0, 0.00),
            (0.3, 0.37),
            (0.6, 0.87),
            (0.9, 1.40),
            (1.2, 1.89),
            (1.5, 2.24),
            (1.8, 2.48),
            (2.1, 2.63),
            (2.4, 2.70),
            (2.7, 2.70),
            (3.0, 2.70),
            (3.3, 2.71),
            (3.6, 2.77),
            (3.9, 2.91),
            (4.2, 3.20),
            (4.5, 3.62),
            (4.8, 4.08),
            (5.1, 4.43),
            (5.4, 4.70),
            (5.7, 4.90),
            (6.0, 5.00)
        ]
        self.assertListEqual(data, control)

    def test_runoff_depth(self):
        rainfall_dist = distributions.Distribution(self.ratio_pairs)
        hydrograph = rainfall_dist.scaled_by(x=6.0, y=5.0)
        data = hydrograph.data
        rounded_data = []
        for line in data:
            runoff_depth = self.basin.runoff_depth(line[1])
            rounded_data.append((round(line[0], 1), round(runoff_depth, 2)))
        control = [
            (0.0, 0.00),
            (0.3, 0.00),
            (0.6, 0.12),
            (0.9, 0.39),
            (1.2, 0.72),
            (1.5, 0.98),
            (1.8, 1.16),
            (2.1, 1.28),
            (2.4, 1.34),
            (2.7, 1.34),
            (3.0, 1.34),
            (3.3, 1.35),
            (3.6, 1.40),
            (3.9, 1.51),
            (4.2, 1.76),
            (4.5, 2.12),
            (4.8, 2.53),
            (5.1, 2.85),
            (5.4, 3.09),
            (5.7, 3.28),
            (6.0, 3.37)
        ]
        self.assertListEqual(rounded_data, control)

    def test_runoff_depth_incremental(self):
        rainfall_dist = distributions.Distribution(self.ratio_pairs)
        rainfall_hydrograph = rainfall_dist.scaled_by(x=6.0, y=5.0)
        data = self.basin.runoff_depth_incremental(rainfall_hydrograph, interval=0.3)
        data = [round(line, 2) for line in data]
        control = [
            0.00,
            0.12,
            0.27,
            0.33,
            0.26,
            0.19,
            0.12,
            0.06,
            0.00,
            0.00,
            0.01,
            0.05,
            0.12,
            0.24,
            0.36,
            0.41,
            0.32,
            0.25,
            0.18,
            0.09
        ]
        self.assertListEqual(data, control)

    def test_flood_hydrograph(self):
        rainfall_dist = distributions.Distribution(self.ratio_pairs)
        rainfall_hydrograph = rainfall_dist.scaled_by(x=6.0, y=5.0)
        hydrograph = self.basin.flood_hydrograph(rainfall_hydrograph, interval=0.3)
        # hydrograph.plot()
        data = [(round(line[0], 1), round(line[1], 0)) for line in hydrograph.data]
        control = [
            (0.0, 0.0),
            (0.3, 0.0),
            (0.6, 17.0),
            (0.9, 89.0),
            (1.2, 273.0),
            (1.5, 585.0),
            (1.8, 971.0),
            (2.1, 1325.0),
            (2.4, 1560.0),
            (2.7, 1628.0),
            (3.0, 1529.0),
            (3.3, 1312.0),
            (3.6, 1058.0),
            (3.9, 844.0),
            (4.2, 730.0),
            (4.5, 769.0),
            (4.8, 987.0),
            (5.1, 1352.0),
            (5.4, 1773.0),
            (5.7, 2131.0),
            (6.0, 2337.0),
            (6.3, 2350.0),
            (6.6, 2177.0),
            (6.9, 1864.0),
            (7.2, 1498.0),
            (7.5, 1148.0),
            (7.8, 849.0),
            (8.1, 615.0),
            (8.4, 444.0),
            (8.7, 323.0),
            (9.0, 234.0),
            (9.3, 170.0),
            (9.6, 123.0),
            (9.9, 90.0),
            (10.2, 65.0),
            (10.5, 48.0),
            (10.8, 35.0),
            (11.1, 25.0),
            (11.4, 18.0),
            (11.7, 12.0),
            (12.0, 7.0),
            (12.3, 4.0),
            (12.6, 2.0),
            (12.9, 1.0),
            (13.2, 0.0),
            (13.5, 0.0)
        ]
        self.assertListEqual(data, control)
