
import numpy as np
from matplotlib import pyplot

from pyflo import networks, links, build


def plot_network_profile(network, link):
    """

    Args:
        network (networks.Network):
        link (links.Link):

    Returns:

    """
    if link not in network.links:
        raise Exception('Link specified must be within the networks links.')
    lnks = build.links_down_from_node(link.node_1, network.links)
    x = 0.0
    inverts = []
    crowns = []
    for l in lnks:
        x1 = x
        if isinstance(l, links.Reach):
            inverts.append((x, l.inverts[0]))
            x += l.length
            inverts.append((x, l.inverts[1]))
        elif isinstance(l, links.Weir):
            inverts.append((x, l.invert))
            x += 10.0  # Update this
        else:
            raise Exception('Link is not valid.')
        if l.section.rise:
            crown = [
                (x1, l.inverts[0] + l.section.rise),
                (x, l.inverts[1] + l.section.rise)
            ]
            crowns.append(crown)
    inverts = np.array(inverts)
    x = inverts[:, 0]
    y = inverts[:, 1]
    pyplot.plot(x, y, 'k')
    for crown in crowns:
        pts = np.array(crown)
        x = pts[:, 0]
        y = pts[:, 1]
        pyplot.plot(x, y, 'k')

    # pyplot.plot(x, y, 'bo')
    pyplot.title(r'Network Profile')
    pyplot.xlabel(r'Position ($ft$)')
    pyplot.ylabel(r'Elevation ($ft$)')
    pyplot.show()
