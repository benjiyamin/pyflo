
import unittest

import numpy as np
from numpy.testing import assert_array_equal
from numpy import genfromtxt

from pyflo import terrain


# class SimpleTerrainTest(unittest.TestCase):
#
#     def setUp(self):
#         a = np.array([
#             [0.0, 0.0, 1.0],
#             [1.0, 0.0, 3.0],
#             [2.0, 0.0, 5.0],
#             [0.0, 1.0, 9.0],
#             [1.0, 1.0, 2.0],
#             [2.0, 1.0, 8.0],
#             [0.0, 2.0, 7.0],
#             [1.0, 2.0, 6.0],
#             [2.0, 2.0, 4.0],
#         ])
#         self.grid = terrain.elevation_grid(a, num=3)
#
#     def test_flow_directions_grid_from_xyz(self):
#         produced = terrain.flow_directions(self.grid)
#         expected = np.array([
#             [0.0, 4.0, 5.0],
#             [2.0, 3.0, 4.0],
#             [1.0, 2.0, 3.0],
#         ])
#         assert_array_equal(produced, expected)
#
#     def test_flow_magnitudes_grid_from_xyz(self):
#         produced = terrain.magnitudes(self.grid)
#         expected = np.array([
#             [9, 1, 1],
#             [1, 6, 1],
#             [1, 1, 1],
#         ])
#         assert_array_equal(produced, expected)
#
#     def test_high_points_grid_from_xyz(self):
#         produced = terrain.high_points(self.grid)
#         expected = np.array([
#             [0, 1, 1],
#             [1, 0, 1],
#             [1, 1, 1],
#         ]).astype(bool)
#         assert_array_equal(produced, expected)


class DonutTerrainTest(unittest.TestCase):

    def setUp(self):
        a = genfromtxt('./tests/datasets/xyz/donut.xyz')
        self.grid = terrain.elevation_grid(a, num=9)

    def test_elevation_grid(self):
        produced = self.grid
        expected = genfromtxt('./tests/datasets/csv/donut_grid.csv', delimiter=',')
        assert_array_equal(produced, expected)

    def test_low_address_center(self):
        produced = terrain.low_address(self.grid, spill_pt=(3, 3))
        expected = (4, 4)
        self.assertTupleEqual(produced, expected)

    def test_low_address_north(self):
        produced = terrain.low_address(self.grid, spill_pt=(1, 4))
        expected = (0, 4)
        self.assertTupleEqual(produced, expected)

    def test_low_address_south(self):
        produced = terrain.low_address(self.grid, spill_pt=(7, 4))
        expected = (8, 4)
        self.assertTupleEqual(produced, expected)

    def test_low_address_west(self):
        produced = terrain.low_address(self.grid, spill_pt=(4, 1))
        expected = (4, 0)
        self.assertTupleEqual(produced, expected)

    def test_low_address_east(self):
        produced = terrain.low_address(self.grid, spill_pt=(4, 7))
        expected = (4, 8)
        self.assertTupleEqual(produced, expected)

    # def test_flow_directions_grid_from_xyz(self):
    #     produced = terrain.flow_directions(self.grid)
    #     expected = genfromtxt('./tests/datasets/csv/donut_directions.csv', delimiter=',')
    #     assert_array_equal(produced, expected)
    
    def test_watershed_shape(self):
        produced = terrain.basin_shape(self.grid, spill_pt=(3, 3))
        expected = genfromtxt('./tests/datasets/csv/donut_shape.csv', delimiter=',').astype(bool)
        assert_array_equal(produced, expected)
