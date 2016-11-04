"""Classes for cross sectional shapes.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import collections
import math


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
        l = self.l_slope * depth**2.0 / 2.0
        c = self.b_width * depth
        r = self.r_slope * depth**2.0 / 2.0
        return l + c + r

    def wet_perimeter(self, depth):
        """Get the wet perimeter of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`

        Returns:
            float: Wet perimeter, in :math:`feet`.

        """
        l = math.sqrt(depth**2.0 * (1.0 + self.l_slope**2.0))
        c = self.b_width
        r = math.sqrt(depth ** 2.0 * (1.0 + self.r_slope ** 2.0))
        return l + c + r

    def surface_width(self, depth):
        l = self.l_slope * depth
        c = self.b_width
        r = self.r_slope * depth
        return l + c + r

    def projection(self, depth):
        return self.surface_width(depth)


class Irregular(Section):

    def __init__(self, points, count=1, **kwargs):
        super(Irregular, self).__init__(count, **kwargs)
        self.points = points

    def get_new_vertices(self, depth):
        """Get the new vertices of the cross section including
            the intersection of ground line with the water surface, given a depth from the
            lowest point.

        Args:
            depth (float): Depth, in :math:`feet`

        Returns:
            list of tuples (float) in (x, y) format

        """

        left = 0                # Water surface intersection at left
        right = 0               # Water surface intersection at right
        new_points = []
        water_elevation = self.get_lowest_elev + depth

        for index in range(len(self.points)):
            x, y = self.points[index]

            # Look for the first point of intersection
            if left == 0:
                if y < water_elevation:
                    left += 1
                    x1 = self.points[index-1][0]
                    y1 = self.points[index-1][1]
                    x2 = self.points[index][0]
                    y2 = self.points[index][1]
                    x3 = (water_elevation - y1) * (x2 - x1) / (y2 - y1) + x1
                    new_points.append((x3, water_elevation))

            if right == 0:
                if left == 1:
                    if y > water_elevation:
                        right += 1
                        x1 = self.points[index-1][0]
                        y1 = self.points[index-1][1]
                        x2 = self.points[index][0]
                        y2 = self.points[index][1]
                        x3 = (water_elevation - y1) * (x2 - x1) / (y2 - y1) + x1
                        new_points.append((x3, water_elevation))

            if left == 1:
                if right == 0:
                    new_points.append(self.points[index])
        return new_points

    def flow_area(self, depth):
        """Get the cross sectional area of flow, given a depth from the lowest point.

        Args:
            depth (float): Depth, in :math:`feet`

        Returns:
            float: Wet area, in :math:`feet`.

        """

        vertices = self.get_new_vertices(depth)
        n = len(vertices)
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += vertices[i][0] * vertices[j][1]
            area -= vertices[j][0] * vertices[i][1]
        area = abs(area) / 2.0
        return area

    def wet_perimeter(self, depth):
        """Get the wet perimeter of flow, given a depth from the lowest point.

        Args:
            depth (float): Depth, in :math:`feet`

        Returns:
            float: Wet perimeter, in :math:`feet`.

        """
        p = 0.0
        new_points = self.get_new_vertices(depth)
        n = len(new_points)
        for i in range(n-1):
            p1 = new_points[i]
            p2 = new_points[i+1]
            p += self.point_distance([p1, p2])

        return p

    def point_distance(self, two_points):
        """Get the distance between two given points.

        Args:
            two_points (float): Depth, in :math:`feet`

        Returns:
            float: Distance between two points, in :math:`feet`.

        """
        p1 = two_points[0]
        p2 = two_points[1]
        x1, y1 = p1
        x2, y2 = p2

        dist = math.sqrt((y2-y1)**2 + (x2-x1)**2)

        return dist

    @property
    def get_lowest_elev(self):
        """Get the elevation of the lowest point of the cross section.

        Args:

        Returns:
            float: Elevation, in :math:`feet`.

        """
        elevs = []                  # List of elevations (ordinates)
        lowest = 0                  # Initial value of lowest
        for point in self.points:
            elevs.append(point[1])  # Iterate through the points and collect the ordinates
        for i in range(len(elevs)):  # Find the lowest in the list of ordinates
            if i == len(elevs):
                break
            if elevs[i] < lowest:
                lowest = elevs[i]
            else:
                lowest = lowest
        return lowest
