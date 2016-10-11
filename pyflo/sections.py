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

    def __init__(self, points, closed=False, count=1, **kwargs):
        super(Irregular, self).__init__(count, **kwargs)
        self.points = points
        self.closed = closed

    @property
    def rise(self):
        if self.closed:
            y_max = max(point[1] for point in self.points)
            y_min = min(point[1] for point in self.points)
            return y_max - y_min
        raise ValueError('Section only has a defined rise property if the closed attribute is True')

    @property
    def upper_i(self):
        return 1 if self.closed else 0

    def flow_area(self, depth):
        """Get the cross sectional area of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`.

        Returns:
            float: Area, in :math:`feet^2`.

        """
        y_min = min(point[1] for point in self.points)
        y_d = y_min + depth
        points = self.points
        if self.points[0][1] < y_d:     # First y value submerged. shift to calc correctly.
            y_max = max(point[1] for point in self.points)
            shift = -self.points.index(y_max)
            items = collections.deque(self.points)
            points = list(items.rotate(shift))
        a_total = 0.0
        a_local = 0.0
        for point_1, point_2 in zip(points, points[1:self.upper_i]):
            x_1, y_1 = point_1
            x_2, y_2 = point_2
            total_up = False
            if y_1 < y_d or y_2 < y_d:
                if y_2 < y_d < y_1:     # Submerging
                    x_1 += (x_2-x_1) * (y_d-y_1) / (y_2-y_1)
                    x_d = x_1
                elif y_1 < y_d < y_2:   # Emerging
                    x_2 = x_1 + (x_2-x_1) * (y_d-y_1) / (y_2-y_1)
                    total_up = True
                a_local += (x_1+x_2) * (y_1-y_2)
                if total_up and x_d:
                    a_local += (x_2+x_d) * (y_2-y_d)
                    a_total += a_local
                    a_local = 0.0
        return a_total

    def wet_perimeter(self, depth):
        """Get the wet perimeter of flow, given a depth from the invert.

        Args:
            depth (float): Depth, in :math:`feet`

        Returns:
            float: Wet perimeter, in :math:`feet`.

        """
        y_min = min(point[1] for point in self.points)
        y_d = y_min + depth
        perimeter = 0.0
        for point_1, point_2 in zip(self.points, self.points[1:self.upper_i]):
            x_1, y_1 = point_1
            x_2, y_2 = point_2
            if y_1 < y_d or y_2 < y_d:
                if y_2 < y_d < y_1:     # Submerging
                    x_1 += (x_2-x_1) * (y_d-y_1) / (y_2-y_1)
                elif y_1 < y_d < y_2:   # Emerging
                    x_2 = x_1 + (x_2-x_1) * (y_d-y_1) / (y_2-y_1)
                perimeter += math.hypot(x_2 - x_1, y_2 - y_1)
        return perimeter

    def surface_width(self, depth):
        i_points = self.intersection_points(depth)
        width = 0.0
        a = iter(i_points)  # Pairwise iterator
        for point_1, point_2 in zip(a, a):
            width += point_2[0] - point_1[0]
        return width

    def projection(self, depth):
        y_min = min(point[1] for point in self.points)
        y_d = y_min + depth
        projection = 0.0
        for point_1, point_2 in zip(self.points, self.points[1:self.upper_i]):
            x_1, y_1 = point_1
            x_2, y_2 = point_2
            if y_1 < y_d or y_2 < y_d:
                if y_2 < y_d < y_1:     # Submerging
                    x_1 += (x_2-x_1) * (y_d-y_1) / (y_2-y_1)
                elif y_1 < y_d < y_2:   # Emerging
                    x_2 = x_1 + (x_2-x_1) * (y_d-y_1) / (y_2-y_1)
                projection += x_2 - x_1
        return projection

    def intersection_points(self, depth):
        y_min = min(point[1] for point in self.points)
        y_d = y_min + depth
        i_points = []
        for point_1, point_2 in zip(self.points, self.points[1:self.upper_i]):
            x_1, y_1 = point_1
            x_2, y_2 = point_2
            if min(y_1, y_2) < y_d < max(y_1, y_2):
                x_int = x_1 + (x_2-x_1) * (y_d-y_1) / (y_2-y_1)
                i_points.append((x_int, y_d))
        return sorted(i_points, key=lambda point: point[0])
