"""Classes for network design and simple reach-based hydraulics.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import itertools

from pyflo import links, sections, basins


class Node(object):

    def __init__(self, network):
        """A point where a :class:`Basin`, :class:`Reach`, or :class:`Reservoir` can be assigned.

        Args:
            network (Network): The parent.

        """
        self.network = network
        self.reach = None
        self.links = []
        self.basin = None
        self.reservoir = None

    def create_reach(self, node_2, invert_1, invert_2, length, section):
        """Create a new :class:`Reach` and assign the node to the upstream end.

        Args:
            node_2 (Node): The node to link at the downstream end.
            invert_1 (float): The reach bottom elevation at the upstream end, in :math:`feet`.
            invert_2 (float): The reach bottom elevation at the downstream end, in :math:`feet`.
            length (float): The total longitudinal distance, end-to-end, in :math:`feet`.
            section (sections.Section): The cross sectional shape.

        Returns:
            hydra.links.Reach: The created instance.

        """
        reach = links.Reach(invert_1, invert_2, length, section, node_1=self, node_2=node_2)
        self.reach = reach
        self.links.append(reach)
        return reach

    def create_weir(self, node_2, invert, k_orif, k_weir, section):
        """Create a new :class:`Weir` and assign the node to the upstream end.

        Args:
            node_2 (Node): The node to link at the downstream end.
            invert (float): The opening bottom elevation, in :math:`feet`.
            k_orif (float): The coefficient used for orifice flow, when the opening is submerged.
            k_weir (float): The coefficient used for weir flow, when the opening is not submerged.
            section (sections.Section): The cross sectional shape.

        Returns:
            links.Weir: The created instance.

        """
        weir = links.Weir(invert, k_orif, k_weir, section, node_1=self, node_2=node_2)
        self.links.append(weir)
        return weir

    def add_reach(self, reach):
        """Assign a :class:`Reach` instance as a child of the node.

        Args:
            reach (links.Reach): The instance to add.

        Warning:
            If a reach is currently assigned to the node, it will be overwritten.

        """
        reach.node_1 = self
        self.links.append(reach)
        self.reach = reach

    def add_link(self, link):
        link.node_1 = self
        self.links.append(link)

    def add_basin(self, basin):
        """Assign a :class:`Basin` instance as a child of the node.

        Args:
            basin (basins.Basin): The instance to add.

        Warning:
            If a basin is currently assigned to the node, it will be overwritten.

        """
        self.basin = basin

    def add_reservoir(self, reservoir):
        self.reservoir = reservoir


class Network(object):

    def __init__(self):
        """A top level container for storing network components"""
        self.nodes = []

    @property
    def links(self):
        lists = [node.links for node in self.nodes]
        return list(itertools.chain.from_iterable(lists))

    @property
    def reaches(self):
        return [node.reach for node in self.nodes if node.reach]

    @property
    def basins(self):
        return [node.basin for node in self.nodes if node.basin]

    def create_node(self):
        """Create a new :class:`Node` instance and house it as a child of the network.

        Returns:
            Node: The created instance.

        """
        node = Node(self)
        self.nodes.append(node)
        return node

    def add_node(self, node):
        """Add a :class:`Node` instance to the network and house it as a child of the network."""
        node.network = self
        self.nodes.append(node)
