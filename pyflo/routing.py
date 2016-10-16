"""Classes for performing storage based analysis with timed simulations.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import math
from typing import List, Tuple, Dict

import numpy as np
from scipy import optimize, interpolate

from pyflo import build, links, networks


class Tailwater(object):

    def __init__(self, time_stages):
        """Represents a relationship between elevation at any given time.

        Args:
            time_stages (List[Tuple[float, float]]): Pairs of time (in :math:`hours`) and elevation
                (in :math:`feet`).

        Raises:
            ValueError: If any of the times in time_stages are negative.

        """
        if min(time_stage[0] for time_stage in time_stages) < 0.0:
            raise ValueError('Times in time_stages must all be positive numbers.')
        self.time_stages = time_stages

    def stage(self, time):
        """Get the elevation that corresponds to a time.

        Args:
            time (float): In :math:`hours`.

        Returns:
            float: Elevation, in :math:`feet`.

        Notes:
            - If time is below the minimum time_stage, the lowest stage will be used.
            - If time is above the maximum time_stage, the highest stage will be used.

        """
        if self.time_stages:
            pairs = sorted(self.time_stages, key=lambda time_stage: time_stage[0])
            x_col, y_col = zip(*pairs)
            fill_value = (y_col[0], y_col[-1])
            y_interp = interpolate.interp1d(x_col, y_col, bounds_error=False, fill_value=fill_value)
            return y_interp(time)
        return 0.0


class Reservoir(object):

    def __init__(self, contours, start_stage=None, **kwargs):
        """Represents the 3D geometry of a 'bowl' shaped rainwater collector.

        Args:
            contours (List[Tuple[float, float]]): Pairs of elevation (in :math:`feet`) and area
                (in :math:`feet^2`).
            start_stage (float): The initial elevation where water stage is located at time 0,
                in :math:`feet`.

        """
        self.contours = sorted(contours, key=lambda contour: contour[0])
        if not start_stage:
            start_stage = self.contours[0][0]
        self.start_stage = start_stage
        self.node = kwargs.pop('node', None)

    def area(self, stage):
        """Get an area that corresponds to the defined elevation.

        Args:
            stage (float): An elevation, in :math:`feet`.

        Returns:
            float: Area, in :math:`feet^2`.

        Note:
            If elevation is above the maximum contour elevation, the area will be extrapolated.

        """
        if self.contours:
            pairs = sorted(self.contours, key=lambda contour: contour[0])
            x_col, y_col = zip(*pairs)
            fill_value = 'extrapolate' if stage > x_col[-1] else np.nan
            y_interp = interpolate.interp1d(x_col, y_col, fill_value=fill_value)
            return y_interp(stage)
        return 0.0

    def storage(self, stage=None):
        """Get an volume that corresponds to the defined elevation.

        Args:
            stage (float): An elevation, in :math:`feet`.

        Returns:
            float: Volume, in :math:`feet^3`.

        Note:
            If elevation is above the maximum contour elevation, the volume will be extrapolated.

        """
        if not stage:
            stage = self.start_stage
        storage = 0.0
        if self.contours and stage > min(c[0] for c in self.contours):
            pairs = [c for c in self.contours if c[0] < stage]
            pairs.sort(key=lambda x: x[0])
            pairs.append((stage, self.area(stage)))
            for pair_1, pair_2 in zip(pairs, pairs[1:]):
                stage_1, area_1 = pair_1
                stage_2, area_2 = pair_2
                storage += (area_2+area_1) / 2.0 * (stage_2-stage_1)
        return storage

    def stage_accuracy(self, stage, storage):
        """Check solution convergence for stage's corresponding volume and storage.

        Args:
            stage (float): An elevation, in :math:`feet`.
            storage (float): A volume, in :math:`feet^3`.

        Returns:
            float: The difference between stage's corresponding volume and storage.

        """
        return self.storage(stage) - storage

    def stage(self, storage):
        """Goal seek the elevation that corresponds to a defined volume.

        Args:
            storage (float): A volume, in :math:`feet^3`.

        Returns:
            float: Elevation, in :math:`feet`.

        """
        if self.contours:
            contours = sorted(self.contours, key=lambda x: x[0])
            bound_1 = contours[0][0]
            bound_2 = contours[-1][0]
            stage = optimize.bisect(
                f=self.stage_accuracy,
                a=bound_1,
                b=bound_2,
                args=(storage,)
            )
            return stage
        return self.start_stage


class Analysis(object):

    def __init__(self, node, tw, duration, interval, rain_dist=None):
        """

        Args:
            node (networks.Node):
            tw (float):
            duration (float):
            interval (float):
            rain_dist (distributions.Distribution):

        """
        self.node = node
        self.tw = tw
        self.duration = duration                        # hours
        self.interval = interval                        # hours
        self.rain_dist = rain_dist

    def init_node_solution_results(self):
        """

        Returns:
            List[Dict]

        """
        links_ord = build.links_up_from_node(self.node, self.node.network.links)
        results = []
        for link in links_ord:
            hydrograph_data = None
            if link.node_1.basin and self.rain_dist:
                flood_hydrograph = link.node_1.basin.flood_hydrograph(self.rain_dist, self.interval)
                hydrograph_data = flood_hydrograph.data
            stage = link.node_1.reservoir.start_stage if link.node_1.reservoir else self.tw
            storage = link.node_1.reservoir.storage(stage) if link.node_1.reservoir else 0.0
            line = {
                'link': link,
                'hydrograph_data': hydrograph_data,
                'data': [
                    {'time': 0.0, 'inflow': 0.0, 'outflow': 0.0, 'storage': storage, 'stage': stage}
                ]
            }
            results.append(line)
        return results

    def stage_accuracy(self, stage, inflow, link, results):
        result = [result for result in results if result['link'] == link][0]
        data = result['data']
        line = data[-1]
        inflow_1 = line['inflow']
        outflow_1 = line['outflow']
        storage_1 = line['storage']
        storage_2 = link.node_1.reservoir.storage(stage) if link.node_1.reservoir else 0.0
        if link.node_2 == self.node:
            tw = self.tw
        else:
            tw = [r['data'][-1]['stage'] for r in results if r['link'].node_1 == link.node_2][0]
        outflow_2 = link.flow(stage, tw)
        inflow_ave = (inflow_1+inflow) / 2.0
        outflow_ave = (outflow_1+outflow_2) / 2.0
        storage_delta_1 = storage_2 - storage_1
        storage_delta_2 = (inflow_ave-outflow_ave) * self.interval * 60.0 * 60.0
        return storage_delta_1 - storage_delta_2

    def stage(self, inflow, link, results):
        """

        Args:
            inflow (float):
            link (links.Link):
            results (List[Dict]):

        Returns:
            List[Dict]:

        """
        stage = optimize.bisect(
            f=self.stage_accuracy,
            a=16.0,
            b=29.8,
            args=(inflow, link, results)
        )
        return stage

    def node_solution_results(self):
        results = self.init_node_solution_results()
        time_steps = math.ceil(self.duration / self.interval)
        for i in range(1, time_steps + 1):
            time = i * self.interval
            for j in results:
                link = j['link']
                data = j['data']
                hydrograph_data = j['hydrograph_data']
                inflow = hydrograph_data[i][1] if hydrograph_data else 0.0
                stage = self.stage(inflow, link, results)

                ds_query = [k for k in results if k['link'].node_1 == link.node_2]
                if link.node_2 == self.node:
                    tw = self.tw
                elif ds_query:
                    ds_result = ds_query[0]
                    ds_data = ds_result['data']
                    ds_line = ds_data[-1]
                    tw = ds_line['stage']
                else:
                    tw = link.invert_2

                storage = link.node_1.reservoir.storage(stage) if link.node_1.reservoir else 0.0
                outflow = link.flow(stage, tw)
                line = {
                    'time': time,
                    'inflow': inflow,
                    'outflow': outflow,
                    'storage': storage,
                    'stage': stage
                }
                data.append(line)
                if ds_query:
                    ds_result = ds_query[0]
                    ds_link = ds_result['link']
                    if ds_link.node_1.reservoir:
                        ds_data = ds_result['data']
                        ds_line = ds_data[-1]
                        ds_storage = ds_line['storage'] + outflow * self.interval * 60.0 * 60.0
                        ds_line['storage'] = ds_storage
                        ds_line['stage'] = ds_link.node_1.reservoir.stage(ds_storage)
        return results
