"""Functions for network building.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import copy
from typing import List

from pyflo import networks


def links_up_from_node(node, links):
    """Gets a list of links traced upstream from a node, ordered from closest to farthest.

    Args:
        node (networks.Node): The most downstream node that links will be traced upstream.
        links (List[pyflo.links.Link]): Available links.

    Returns:
        List[pyflo.links.Link]: A list of links, ordered upstream from node.

    Example:
        Given a system::

            S-6 → S-8 → OUT
                   ↑
            S-4 → S-7
                   ↑
                  S-5

            | >>> ordered_links = links_up_from_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-8', 'S-6', 'S-7', 'S-4', 'S-5']

    """
    trigger = True
    nodes_ds = [node]
    links_out = []
    links_in = copy.copy(links)
    while trigger:
        trigger = False
        for node in nodes_ds:
            for i, link in enumerate(links_in):
                if link.node_2 == node and link.node_1 not in nodes_ds:
                    nodes_ds.append(link.node_1)
                    links_out.append(links_in.pop(i))
                    trigger = True
    return links_out


def links_down_to_node(node, links):
    """Gets a list of links traced downstream to a node, ordered from farthest to closest.

    Args:
        node (networks.Node): The most downstream node that links will be traced downstream.
        links (List[pyflo.links.Link]): Available links.

    Returns:
        List[pyflo.links.Link]: A list of links, ordered downstream to node.

    Example:
        Given a system::

            S-6 → S-8 → OUT
                   ↑
            S-4 → S-7
                   ↑
                  S-5

            | >>> ordered_links = links_down_to_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-5', 'S-4', 'S-7', 'S-6', 'S-8']

    """
    links_out = links_up_from_node(node, links)
    links_out.reverse()
    return links_out


def links_down_from_node(node, links):
    """Gets a list of links traced downstream from a node, ordered from closest to farthest.

    Args:
        node (networks.Node): The most upstream node that links will be traced downstream.
        links (List[pyflo.links.Link]): Available links.

    Returns:
        List[pyflo.links.Link]: A list of links, ordered downstream from node.

    Example:
        Given a system::

            S-6 → S-8 → OUT
                   ↑
            S-4 → S-7
                   ↑
                  S-5

            | >>> ordered_links = links_down_from_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-4', 'S-7', 'S-8']

    """
    links_out = []
    node_curr = node
    trigger = True
    links_in = copy.copy(links)
    while trigger:
        trigger = False
        for i, link in enumerate(links_in):
            if link.node_1 == node_curr:
                links_out.append(links_in.pop(i))
                node_curr = link.node_2
                trigger = True
    return links_out


def links_up_to_node(node, links):
    """Gets a list of links traced upstream to a node, ordered from farthest to closest.

    Args:
        node (networks.Node): The most upstream node that links will be traced upstream.
        links (List[pyflo.links.Link]): Available links.

    Returns:
        List[pyflo.links.Link]: A list of links, ordered upstream to node.

    Example:
        Given a system::

            S-6 → S-8 → OUT
                   ↑
            S-4 → S-7
                   ↑
                  S-5

            | >>> ordered_links = links_up_to_node(a_node, some_links)
            | >>> print([link.display_name for link in ordered_links])
            | ['S-8', 'S-7', 'S-6']

    """
    links_out = links_down_from_node(node, links)
    links_out.reverse()
    return links_out
