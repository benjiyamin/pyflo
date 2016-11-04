
import unittest

from pyflo import networks as nw
from pyflo import build, sections


class BuildTest(unittest.TestCase):

    def test_reaches_ordered_up_from_node(self):
        network = nw.Network()
        s102 = network.create_node()
        s101 = network.create_node()
        o1_1 = network.create_node()
        rc18 = sections.Circle(diameter=1.5, mannings=0.012)
        p101 = s101.create_reach(node_2=s102, inverts=(8.0, 7.0), length=300.0, section=rc18)
        p102 = s102.create_reach(node_2=o1_1, inverts=(7.0, 6.0), length=300.0, section=rc18)
        reaches = [node.reach for node in network.nodes if node.reach]
        produced = build.links_up_from_node(o1_1, reaches)
        expected = [p102, p101]
        self.assertEqual(produced, expected)

    def test_reaches_ordered_down_to_node(self):
        network = nw.Network()
        s102 = network.create_node()
        s101 = network.create_node()
        o1_1 = network.create_node()
        rc18 = sections.Circle(diameter=1.5, mannings=0.012)
        p101 = s101.create_reach(node_2=s102, inverts=(8.0, 7.0), length=300.0, section=rc18)
        p102 = s102.create_reach(node_2=o1_1, inverts=(7.0, 6.0), length=300.0, section=rc18)
        reaches = [node.reach for node in network.nodes if node.reach]
        produced = build.links_down_to_node(o1_1, reaches)
        expected = [p101, p102]
        self.assertEqual(produced, expected)
