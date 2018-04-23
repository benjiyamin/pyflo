"""Classes for cross sectional shapes.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import math
from typing import List, Tuple


class Section(object):

    def __init__(self, count=1, **kwargs):
        self.count = count
        self.n = kwargs.pop('n', None)

    @property
    def rise(self):
        return

    @rise.setter
    def rise(self, value):
        return

    def hyd_radius(self, depth):
        """Get the hydraulic radius of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`.

        Returns:
            float: Hydraulic radius, in :math:`feet`.

        """
        p_w = self.wet_perimeter(depth)
        if p_w > 0.0:
            a_f = self.flow_area(depth)
            r_h = a_f / p_w
            return r_h
        return 0.0

    def flow_area(self, depth):
        return 0.0

    def wet_perimeter(self, depth):
        return 0.0

    def surface_width(self, depth):
        pass

    def projection(self, depth):
        pass


class Circle(Section):

    def __init__(self, diameter, count=1, **kwargs):
        super(Circle, self).__init__(count, **kwargs)
        self.diameter = diameter

    @property
    def rise(self):
        return self.diameter

    @rise.setter
    def rise(self, value):
        self.diameter = value

    def flow_area(self, depth):
        """Get the cross sectional area of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`.

        Returns:
            float: Area, in :math:`feet^2`.

        """
        d_calc = min(depth, self.diameter)
        alpha = 2.0 * math.acos(1.0 - 2.0 * d_calc / self.diameter)
        return self.count * self.diameter**2.0 / 8.0 * (alpha - math.sin(alpha))

    def wet_perimeter(self, depth):
        """Get the wet perimeter of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`

        Returns:
            float: Wet perimeter, in :math:`feet`.

        """
        d_calc = min(depth, self.diameter)
        alpha = 2.0 * math.acos(1.0 - 2.0 * d_calc / self.diameter)
        return self.count * alpha * self.diameter / 2.0

    def surface_width(self, depth):
        d_calc = min(depth, self.diameter)
        alpha = 2.0 * math.acos(1.0 - 2.0 * d_calc / self.diameter)
        return self.count * self.diameter * math.sin(alpha / 2.0)

    def projection(self, depth):
        if depth < self.rise / 2.0:
            d_calc = min(depth, self.diameter)
            return self.surface_width(d_calc)
        return self.diameter


class Rectangle(Section):

    def __init__(self, span, rise, count=1, **kwargs):
        super(Rectangle, self).__init__(count, **kwargs)
        self.span = span
        self._rise = rise

    @property
    def rise(self):
        return self._rise

    @rise.setter
    def rise(self, value):
        self._rise = value

    @property
    def perimeter(self):
        return 2.0*self.span + 2.0*self.rise

    def flow_area(self, depth):
        d_calc = min(depth, self.rise)
        return d_calc * self.span

    def wet_perimeter(self, depth):
        if depth < self.rise:
            return self.span + 2.0*depth
        return self.perimeter

    def surface_width(self, depth):
        return self.span

    def projection(self, depth):
        return self.span


class Square(Rectangle):

    def __init__(self, side, count=1, **kwargs):
        super(Square, self).__init__(side, side, count, **kwargs)
        self.side = side

    @property
    def rise(self):
        return self._rise

    @rise.setter
    def rise(self, value):
        self._rise = value
        self.side = value


class Trapezoid(Section):

    def __init__(self, l_slope, b_width, r_slope, count=1, **kwargs):
        super(Trapezoid, self).__init__(count, **kwargs)
        self.l_slope = l_slope
        self.b_width = b_width
        self.r_slope = r_slope

    def flow_area(self, depth):
        """Get the cross sectional area of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`.

        Returns:
            float: Area, in :math:`feet^2`.

        """
        l = depth**2.0 / 2.0 / self.l_slope
        c = self.b_width * depth
        r = depth**2.0 / 2.0 / self.r_slope
        return l + c + r

    def wet_perimeter(self, depth):
        """Get the wet perimeter of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`.

        Returns:
            float: Wet perimeter, in :math:`feet`.

        """
        l = math.sqrt(depth**2.0 * (1.0 + (1.0/self.l_slope)**2.0))
        c = self.b_width
        r = math.sqrt(depth**2.0 * (1.0 + (1.0/self.r_slope)**2.0))
        return l + c + r

    def surface_width(self, depth):
        l = depth / self.l_slope
        c = self.b_width
        r = depth / self.r_slope
        return l + c + r

    def projection(self, depth):
        return self.surface_width(depth)


class Irregular(Section):

    def __init__(self, points, count=1, **kwargs):
        super(Irregular, self).__init__(count, **kwargs)
        self.points = points

    def flow_vertices(self, depth):
        """Get the new vertices of the cross section including the intersection of ground line with
            the water surface, given a depth from the lowest point.

        Args:
            depth (float): Depth, in :math:`feet`.

        Returns:
            List[Tuple[float, float]]: The updated vertices (points).

        """
        left = 0                                    # Water surface intersection at left
        right = 0                                   # Water surface intersection at right
        points = []
        elev_water = self.elev_lowest + depth

        for i, pt in enumerate(self.points):
            x2, y2 = pt
            pt_prev = self.points[i - 1]
            x1, y1 = pt_prev

            if left == 0 and y2 < elev_water:
                left += 1
                x3 = (elev_water-y1) * (x2-x1) / (y2-y1) + x1
                points.append((x3, elev_water))

            if left == 1 and right == 0:
                if y2 > elev_water:
                    right += 1
                    x3 = (elev_water-y1) * (x2-x1) / (y2-y1) + x1
                    points.append((x3, elev_water))
                else:
                    points.append(pt)
        return points

    def flow_area(self, depth):
        """Get the cross sectional area of flow, given a depth from the lowest point.

        Args:
            depth (float): Depth, in :math:`feet`.

        Returns:
            float: Wet area, in :math:`feet^2`.

        """

        vertices = self.flow_vertices(depth)
        area = 0.0
        for i, v in enumerate(vertices):
            n = len(vertices)
            j = (i + 1) % n
            x1, y1 = v
            x2, y2 = vertices[j]
            area += x1 * y2
            area -= x2 * y1
        return abs(area) / 2.0

    def wet_perimeter(self, depth):
        """Get the wet perimeter of flow, given a depth from the lowest point.

        Args:
            depth (float): Depth, in :math:`feet`

        Returns:
            float: Wet perimeter, in :math:`feet`.

        """
        perimeter = 0.0
        vertices = self.flow_vertices(depth)
        for pt1, pt2 in zip(vertices, vertices[1:]):
            x1, y1 = pt1
            x2, y2 = pt2
            perimeter += math.hypot(x2 - x1, y2 - y1)
        return perimeter

    @property
    def elev_lowest(self):
        """Get the elevation of the lowest point of the cross section.

        Returns:
            float: Elevation, in :math:`feet`.

        """
        return min(pt[1] for pt in self.points)
