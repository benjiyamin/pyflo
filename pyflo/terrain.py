"""Functions for creating, analyzing, and manipulating 3D geometry.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

from typing import Tuple

from scipy import ndimage
from matplotlib.mlab import griddata
import numpy


C = 0
N = 2
W = 4
S = 6
E = 8

NE = 1
NW = 3
SW = 5
SE = 7


def elevation_grid(array, num=50):
    """Create a mesh of elevation values interpolated from an array of (x, y, z) points.

    Args:
        array (numpy.ndarray): An array of (x, y, z) points.
        num (int): Number of samples to generate in each the x and y directions. Default is 50. Must
            be non-negative.

    Returns:
        numpy.ndarray: An array of elevation values.

    """
    x, y, z = array[:, 0], array[:, 1], array[:, 2]
    xi = numpy.linspace(min(x), max(x), num=num)
    yi = numpy.linspace(min(y), max(y), num=num)
    grid = griddata(x, y, z, xi, yi, interp='linear')
    return grid


def low_address(grid, spill_pt):
    """Get the lowest value a spill point is connected to in terms of lower elevations.

    Args:
        grid (numpy.ndarray): An array of elevation values.
        spill_pt (Tuple[int, int]): The address of the spill point within the grid formatted as
            such a tuple with the format (row index, column index).

    Returns:
        Tuple[int, int]: The address of the lowest point the spill point is connected to in terms of
            lower elevations.

    """
    grid = numpy.array(grid)
    queue = spill_pt
    nrows, ncols = grid.shape
    while queue:
        row_i, col_i = queue
        row_lower, row_upper = max(0, row_i - 1), min(row_i+2, nrows)
        col_lower, col_upper = max(0, col_i - 1), min(col_i+2, ncols)
        z = grid[row_lower:row_upper, col_lower:col_upper]
        min_value = numpy.nanmin(z)
        if grid[row_i, col_i] != min_value:
            if grid[row_i-1][col_i] == min_value:
                # d = N
                row_i -= 1
            elif grid[row_i, col_i-1] == min_value:
                # d = W
                col_i -= 1
            elif grid[row_i+1, col_i] == min_value:
                # d = S
                row_i += 1
            elif grid[row_i, col_i+1] == min_value:
                # d = E
                col_i += 1
            elif grid[row_i-1, col_i+1] == min_value:
                # d = NE
                row_i -= 1
                col_i += 1
            elif grid[row_i-1, col_i-1] == min_value:
                # d = NW
                row_i -= 1
                col_i -= 1
            elif grid[row_i+1, col_i-1] == min_value:
                # d = SW
                row_i += 1
                col_i -= 1
            elif grid[row_i+1, col_i+1] == min_value:
                # d = SE
                row_i += 1
                col_i += 1
            queue = row_i, col_i
        else:
            return queue


def basin_shape(grid, spill_pt):
    """Get an array of booleans that identifies which cells are part of the same basin as a given
    spill point.

    Args:
        grid (numpy.ndarray): An array of elevation values.
        spill_pt (Tuple[int, int]): The address of the spill point within the grid formatted as
            such a tuple with the format (row index, column index).

    Returns:
        numpy.ndarray: An array of boolean values. Cells marked true are part of the same basin as a
            the input spill point.

    """
    grid = numpy.array(grid)
    neighbors = [(-1, -1), (-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1)]
    b = numpy.zeros(grid.shape).astype(bool)
    row_start, col_start = low_address(grid, spill_pt)
    queue = [(row_start, col_start)]  # push start coordinate on stack
    nrows, ncols = grid.shape
    while queue:
        row_i, col_i = queue.pop()
        b[row_i, col_i] = True
        for row_d, col_d in neighbors:
            row_n, col_n = row_i + row_d, col_i + col_d
            if 0 <= row_n < nrows and 0 <= col_n < ncols and not b[row_n, col_n]:
                if grid[row_n, col_n] >= grid[row_i, col_i]:
                    queue.append((row_n, col_n))
    return b


def basin_area(grid, row_spill, col_spill):
    pass


# def flow_direction(array):
#     min_value = numpy.nanmin(array)
#     if array[4] == min_value:
#         d = C
#     elif array[1] == min_value:
#         d = N
#     elif array[3] == min_value:
#         d = W
#     elif array[7] == min_value:
#         d = S
#     elif array[5] == min_value:
#         d = E
#     elif array[2] == min_value:
#         d = NE
#     elif array[0] == min_value:
#         d = NW
#     elif array[6] == min_value:
#         d = SW
#     elif array[8] == min_value:
#         d = SE
#     else:
#         raise ValueError
#     return d
#
#
# def flow_directions(grid):
#     d = ndimage.generic_filter(grid, flow_direction, size=3, mode='constant', cval=numpy.nan)
#     return d
#
#
# def magnitudes(grid):
#     a = flow_directions(grid)
#     b = numpy.zeros(a.shape).astype(int)
#     for i, x in enumerate(a):
#         for j, y in enumerate(x):
#             trigger = False
#             row_i, col_i = i, j
#             while not trigger:
#                 z = a[row_i, col_i]
#                 if z >= 0:
#                     b[row_i, col_i] += 1
#                     if z == NW:
#                         row_i -= 1
#                         col_i -= 1
#                     elif z == N:
#                         row_i -= 1
#                     elif z == NE:
#                         row_i -= 1
#                         col_i += 1
#                     elif z == W:
#                         col_i -= 1
#                     elif z == E:
#                         col_i += 1
#                     elif z == SW:
#                         row_i += 1
#                         col_i -= 1
#                     elif z == S:
#                         row_i += 1
#                     elif z == SE:
#                         row_i += 1
#                         col_i += 1
#                     else:
#                         trigger = True
#                 else:
#                     trigger = True
#     return b
#
#
# def high_points(grid):
#     a = magnitudes(grid)
#     b = a <= 1
#     return b
