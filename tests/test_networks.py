
import unittest

from pyflo import sections, networks, links
from pyflo.rational import hydraulics, hydrology


class NetworkTest(unittest.TestCase):

    def test_cumulative_runoff_data(self):
        network = networks.Network()
        s102 = network.create_node()
        s101 = network.create_node()
        o1_1 = network.create_node()
        rc18 = sections.Circle(diameter=1.5, mannings=0.012)
        r1 = s101.create_reach(node_2=s102, invert_1=8.0, invert_2=7.0, length=300.0, section=rc18)
        r2 = s102.create_reach(node_2=o1_1, invert_1=7.0, invert_2=6.0, length=300.0, section=rc18)
        b101 = hydrology.Basin(tc=10.0, area=0.1, c=0.95)
        b102 = hydrology.Basin(tc=10.0, area=0.2, c=0.95)
        s101.add_basin(b101)
        s102.add_basin(b102)
        basin_data = hydraulics.totaled_basin_data(o1_1)
        control_area_1 = b101.area
        control_area_2 = control_area_1 + b102.area
        control_runoff_1 = b101.runoff_area
        control_runoff_2 = control_runoff_1 + b102.runoff_area
        result_area_1 = basin_data[r1]['area']
        result_area_2 = basin_data[r2]['area']
        result_runoff_1 = result_area_1 * basin_data[r1]['c']
        result_runoff_2 = result_area_2 * basin_data[r2]['c']
        expected = (control_area_1, control_area_2, control_runoff_1, control_runoff_2)
        produced = (result_area_1, result_area_2, result_runoff_1, result_runoff_2)
        # self.assertEqual(produced, expected)
        self.assertTupleEqual(produced, expected)

    def test_same_node_reach_from_func(self):
        network = networks.Network()
        s101 = network.create_node()
        with self.assertRaises(ValueError):
            rc18 = sections.Circle(diameter=1.5, mannings=0.012)
            s101.create_reach(node_2=s101, invert_1=8.0, invert_2=7.0, length=300.0, section=rc18)

    def test_same_node_reach_from_init(self):
        network = networks.Network()
        s101 = network.create_node()
        with self.assertRaises(ValueError):
            rc18 = sections.Circle(diameter=1.5, mannings=0.012)
            links.Reach(node_1=s101, node_2=s101, invert_1=8.0, invert_2=7.0, length=300.0,
                        section=rc18)
