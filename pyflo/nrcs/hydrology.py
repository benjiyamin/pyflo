"""Classes for performing NRCS (SCS) unit hydrograph method basin hydrology analysis.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import numpy

from pyflo import basins, distributions


class Basin(basins.Basin):

    def __init__(self, area, cn, tc, runoff_dist, peak_factor, **kwargs):
        """A watershed draining to a node with hydrology attributes, dimensions, and methods.

        Args:
            area (float): The delineated region concentrating to a point, in :math:`acres`.
            cn (float): An empirical parameter for predicting direct runoff.
            tc (float): The estimated time of concentration, in :math:`minutes`.
            runoff_dist (numpy.ndarray): The unscaled unit hydrograph runoff distribution.
            peak_factor (float): A value for scaling peak runoff.

        """
        super(Basin, self).__init__(area)
        self.cn = cn
        self.tc = tc
        self.runoff_dist = runoff_dist
        self.peak_factor = peak_factor
        shapes = kwargs.pop('shapes', None)
        if shapes:
            self.add_shapes(shapes)

    @property
    def potential_retention(self):
        return 1000.0/self.cn - 10.0

    @property
    def initial_abstraction(self):
        return 0.2 * self.potential_retention

    def add_shapes(self, shapes):
        """Takes a list of (area, cn) tuples, adding to self.area and weighting a new self.c value.

        Args:
            shapes (List[Tuple[float, float]]): A list of (area, cn) pairs.

        """
        a_shp = sum(shp[0] for shp in shapes)
        cn_shp = sum(shp[0] * shp[1] for shp in shapes) / a_shp
        a_tot = self.area + a_shp
        self.cn = (self.area*self.cn + a_shp*cn_shp) / a_tot
        self.area = a_tot

    def runoff_depth(self, rain_depth):
        """Get the depth of runoff generated from a defined rainfall and properties of the basin.

        Args:
            rain_depth (float): In :math:`inches`.

        Returns:
            float: Runoff, in :math:`inches`.

        """
        if rain_depth > self.initial_abstraction:
            a = (rain_depth - self.initial_abstraction)**2.0
            b = rain_depth - self.initial_abstraction + self.potential_retention
            return a / b
        return 0.0

    def runoff_volume(self, rain_depth):
        """Get the volume of runoff generated from a defined rainfall and properties of the basin.

        Args:
            rain_depth (float): In :math:`inches`.

        Returns:
            float: Runoff, in :math:`feet^3`.

        """
        runoff = self.runoff_depth(rain_depth)
        return runoff * self.area * 43560.0 / 12.0

    def runoff_depth_incremental(self, rain_depths, interval):
        """Generate incremental amount of runoff generated from rainfall

        Args:
            rain_depths (numpy.ndarray): A 2D array of scaled rainfall depths over time.
            interval (float): The amount of time the output will increment by.

        Yields:
            float: The next incremental amount of runoff generated from rainfall.

        """
        pairs = distributions.increment(rain_depths, interval).tolist()
        for pair_1, pair_2 in zip(pairs, pairs[1:]):
            time_1, rainfall_1 = pair_1
            time_2, rainfall_2 = pair_2
            runoff_1 = self.runoff_depth(rainfall_1)
            runoff_2 = self.runoff_depth(rainfall_2)
            runoff_delta = runoff_2 - runoff_1
            yield runoff_delta

    def unit_hydrograph(self, interval):
        """Get a hydrograph that represents the time-flow relationship per unit (inch) of depth.

        Args:
            interval (float): The amount of time the output will increment by.

        Returns:
            numpy.ndarray: The hydrograph of potential basin runoff.

        """
        hydrograph = self.runoff_dist * [self.peak_time, self.peak_runoff]
        hydrograph = distributions.increment(hydrograph, interval)
        return hydrograph

    def flood_data(self, rain_depths, interval):
        """Generate pairs of basin runoff flow generated from rainfall over time.

        Args:
            rain_depths (numpy.ndarray): A 2D array of scaled rainfall depths over time.
            interval (float): The amount of time the output will increment by.

        Yields:
            Tuple[float, float]: The next pair of time and runoff flow generated from rainfall.

        """
        rd = self.unit_hydrograph(interval).tolist()
        ri = list(self.runoff_depth_incremental(rain_depths, interval))
        ri.reverse()  # Reversed list utilized for synthesis
        comp_length = len(rd) + len(ri)
        for i in range(comp_length - 1):
            upper = i + 1
            lower = max(upper - len(ri), 0)
            total = sum(ri[j - upper] * rd[j][1] for j in range(lower, upper) if j < len(rd))
            yield i * interval, total

    def flood_hydrograph(self, rain_depths, interval):
        """Get a composite hydrograph of basin runoff generated from rainfall over time.

        Args:
            rain_depths (numpy.ndarray): A 2D array of scaled rainfall depths over time.
            interval (float): The amount of time the output will increment by.

        Returns:
            numpy.ndarray: The composite hydrograph of runoff generated from rainfall.

        """
        data = list(self.flood_data(rain_depths, interval))
        hydrograph = numpy.array(data)
        return hydrograph

    @property
    def peak_time(self):
        delta = 0.133 * self.tc
        lag = 0.6 * self.tc
        return delta/2.0 + lag

    @property
    def peak_runoff(self):
        return self.peak_factor * self.area / self.peak_time  # cfs
