
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


class SimpleBuildTest(unittest.TestCase):
    
    def setUp(self):
        """Example:
            Given a system::

                S-6 → S-8 → OUT
                       ↑
                S-4 → S-7
                       ↑
                      S-5

        """
        
        self.network = nw.Network()
        
        s6 = self.network.create_node()
        s8 = self.network.create_node()
        s4 = self.network.create_node()
        s7 = self.network.create_node()
        s5 = self.network.create_node()
        self.out = self.network.create_node()

        rc18 = sections.Circle(diameter=1.5, mannings=0.012)

        self.r6 = s6.create_reach(s8, rc18)
        self.r8 = s8.create_reach(self.out, rc18)
        self.r4 = s4.create_reach(s7, rc18)
        self.r7 = s7.create_reach(s8, rc18)
        self.r5 = s5.create_reach(s7, rc18)
    
    def test_links_up_from_node(self):
        """

            | >>> ordered_links = links_up_from_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-8', 'S-6', 'S-7', 'S-4', 'S-5']

        """
        produced = build.links_up_from_node(self.out, self.network.links)
        expected = [self.r8, self.r6, self.r7, self.r4, self.r5]
        self.assertListEqual(produced, expected)

    def test_links_down_to_node(self):
        """

            | >>> ordered_links = links_down_to_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-5', 'S-4', 'S-7', 'S-6', 'S-8']

        """
        produced = build.links_down_to_node(self.out, self.network.links)
        expected = [self.r5, self.r4, self.r7, self.r6, self.r8]
        self.assertListEqual(produced, expected)

    def test_links_down_from_node(self):
        """

            | >>> ordered_links = links_down_from_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-4', 'S-7', 'S-8']

        """
        produced = build.links_down_from_node(self.r4.node_1, self.network.links)
        expected = [self.r4, self.r7, self.r8]
        self.assertListEqual(produced, expected)

    def test_links_up_to_node(self):
        """

            | >>> ordered_links = links_up_to_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-8', 'S-7', 'S-6']

        """
        produced = build.links_up_to_node(self.r4.node_1, self.network.links)
        expected = [self.r8, self.r7, self.r4]
        self.assertListEqual(produced, expected)
