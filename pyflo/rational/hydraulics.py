"""Classes for performing network-wide hydraulic analysis.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

from typing import Dict, Union
from collections import OrderedDict

from pyflo import build, constants, networks, distributions, links


def totaled_basin_data(node):
    """Get cumulative basin data for each reach ordered downstream to the node.

    Returns:
        Dict[links.Link]: A dictionary of data associated to each link.
        Each line of data is a dictionary in the form::

            links.Link: {
                'area': float,
                'c': float
            }

    """
    o_links = build.links_down_to_node(node, links=node.network.links)

    # Accumulate c and area, top-down
    data = OrderedDict()
    for link in o_links:
        area = link.node_1.basin.area if link.node_1.basin else 0.0
        runoff = link.node_1.basin.runoff_area if link.node_1.basin else 0.0
        for r, r_data in data.items():
            if link.node_1 == r.node_2:
                area += r_data['area']
                runoff += r_data['area'] * r_data['c']
        c = runoff / area
        data[link] = {'area': area, 'c': c}
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
            Ditch[links.Link]: A dictionary of data associated to each link.
            Each line of data is a dictionary in the form::

                links.Link: {
                    'area': float,
                    'c': float,
                    'second': float,
                    'tc_local': float,
                    'tc_total': float,
                    'flow': float,
                    'hgl_1': float,
                    'hgl_2': float,
                }

        """
        data = totaled_basin_data(self.node)
        last_link = [link for link in self.node.network.links if link.node_2 == self.node][0]
        # data[-1]['hgl_2'] = self.tw
        data[last_link]['hgl_2'] = self.tw
        for link, link_data in data.items():
            tc = 0.0
            if link.node_1.basin:
                tc = link.node_1.basin.tc
            for r, r_data in data.items():
                if link.node_1 == r.node_2:
                    if 'tc_total' in r_data and isinstance(r_data['tc_total'], float):
                        tc = max(tc, r_data['tc_total'])
            link_data['tc_local'] = tc
            if isinstance(self.intensity, distributions.Evaluator):
                i = self.intensity.get_y(tc / 60.0)
            else:
                i = self.intensity
            ca = link_data['c'] * link_data['area']
            flow = i * ca * constants.K_RATIONAL
            depth = link.normal_depth(flow)
            ts = link.section_time(depth, flow)
            link_data['flow'] = flow
            link_data['tc_total'] = tc + ts

        # Trace back HGL, bottom-up
        for link, link_data in reversed(data.items()):
            stage_2 = self.tw
            for r, r_data in data.items():
                if link.node_2 == r.node_1:
                    if 'hgl_1' in r_data and isinstance(r_data['hgl_1'], float):
                        stage_2 = max(stage_2, r_data['hgl_1'])
            flow = link_data['flow']
            link_data['hgl_2'] = link.hgl_2(stage_2, flow)
            link_data['hgl_1'] = link.hgl_1(stage_2, flow)

        return data
