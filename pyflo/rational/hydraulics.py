"""Classes for performing network-wide hydraulic analysis.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

from typing import List, Dict, Union

from pyflo import build, constants, networks, distributions


def totaled_basin_data(node):
    """Get cumulative basin data for each reach ordered downstream to the node.

    Returns:
        List[Dict]: A list of data.
        Each line of data is a dictionary in the form::

            {
                'reach': Reach,
                'area': float,
                'runoff_area': float
            }

    """
    reaches = build.links_down_to_node(node, links=node.network.reaches)

    # Accumulate runoff_area and area, top-down
    data = []
    for reach in reaches:
        area = reach.node_1.basin.area if reach.node_1.basin else 0.0
        runoff = reach.node_1.basin.runoff_area if reach.node_1.basin else 0.0
        if data:
            for line in data:
                line_reach = line['reach']
                if reach.node_1 == line_reach.node_2:
                    area += line['area']
                    runoff += line['runoff_area']
        data.append({'reach': reach, 'area': area, 'runoff_area': runoff})
    return data


class Analysis(object):

    def __init__(self, node, tw, intensity):
        """References a node and carries attributes necessary to perform network hydraulic analysis.

        Args:
            node (networks.Node): The most downstream node that reaches will be analyzed
                upstream from.
            tw (float): The design hydraulic elevation at the node, which will also act as a lower
                limit for HGL.
            intensity (Union[float, distributions.Evaluator]): The rate of rainfall depth for
                hydrology analysis. If a number is defined, the value is directly utilized. If an
                :class:`distributions.Evaluator` class instance is defined, the output from any
                given time of concentration input is used for calculations

        """
        self.node = node
        self.tw = tw
        self.intensity = intensity

    def hgl_solution_data(self):
        """Analyzes hydraulics for each reach in a network and returns result data.

        Returns:
            List[Dict]: A list of data.
            Each line of data is a dictionary in the form::

                {
                    'reach': Reach,
                    'area': float,
                    'runoff_area': float,
                    'second': float,
                    'tc_local': float,
                    'tc_total': float,
                    'flow': float,
                    'hgl_1': float,
                    'hgl_2': float,
                }

        """
        data = totaled_basin_data(self.node)
        data[-1]['hgl_2'] = self.tw

        # Accumulate travel times, top-down
        for line in data:
            tc = 0.0
            reach = line['reach']
            if reach.node_1.basin:
                tc = reach.node_1.basin.tc
            for r in data:
                l_reach = r['reach']
                if reach.node_1 == l_reach.node_2 and isinstance(r['tc_total'], float):
                    tc = max(tc, r['tc_total'])
            line['tc_local'] = tc
            if isinstance(self.intensity, distributions.Evaluator):
                i = self.intensity.get_y(tc / 60.0)
            else:
                i = self.intensity
            ca = line['runoff_area']
            flow = i * ca * constants.K_RATIONAL
            depth = reach.normal_depth(flow)
            time_section = reach.section_time(depth, flow)
            line['flow'] = flow
            line['tc_total'] = tc + time_section

        # Trace back HGL, bottom-up
        for line in reversed(data):
            reach = line['reach']
            tw = self.tw
            for r in data:
                line_reach = r['reach']
                if reach.node_2 == line_reach.node_1 and isinstance(r['hgl_1'], float):
                    tw = max(tw, r['hgl_1'])
            flow = line['flow']
            line['hgl_2'] = reach.hgl_2(tw, flow)
            line['hgl_1'] = reach.hgl_1(tw, flow)

        return data
