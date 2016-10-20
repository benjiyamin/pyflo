"""Classes for network design and simple reach-based hydraulics.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import math

from scipy import optimize

from pyflo import constants, sections


class Link(object):

    def __init__(self, **kwargs):
        self._node_2 = None
        self.node_1 = kwargs.pop('node_1', None)
        self.node_2 = kwargs.pop('node_2', None)

    @property
    def node_2(self):
        return self._node_2

    @node_2.setter
    def node_2(self, value):
        if value and value is self.node_1:
            raise ValueError('Node 2 cannot be the same as Node 1.')
        self._node_2 = value

    def flow(self, stage_1, stage_2):
        pass


class Weir(Link):

    def __init__(self, invert, k_orif, k_weir, section, **kwargs):
        super(Weir, self).__init__(**kwargs)
        self.invert = invert
        self.k_orif = k_orif
        self.k_weir = k_weir
        self.section = section

    def flow(self, stage_1, stage_2):
        flow = 0.0
        if self.section.rise:
            y_top = self.invert + self.section.rise
            y_ctr = self.invert + self.section.rise / 2.0
            if stage_1 > y_top:                                                     # orifice flow
                if stage_2 < self.invert:                                           # free flow
                    h_eff = stage_1 - y_ctr
                else:                                                               # submerged flow
                    h_eff = stage_1 - stage_2
                area = self.section.flow_area(self.section.rise)
                flow = self.k_orif * area * math.sqrt(2.0 * 32.2 * h_eff)
        elif stage_1 > self.invert:                                                 # weir flow
            depth = stage_1 - self.invert
            flow = self.k_weir * self.section.projection(depth) * depth**1.5
            if stage_2 > self.invert:                                               # submerged flow
                flow *= 1.0 - ((stage_2/stage_1)**1.5)**0.385
        return flow


class Reach(Link):

    def __init__(self, invert_1, invert_2, length, section, k_minor=None, **kwargs):
        """A link between two nodes with hydraulic attributes, dimensions, and methods.

        Args:
            invert_1 (float): The bottom elevation at the upstream ("from") end, in :math:`feet`.
            invert_2 (float): The bottom elevation at the downstream ("to") end, in :math:`feet`.
            length (float): The total longitudinal distance, end-to-end, in :math:`feet`.
            section (sections.Section): The cross sectional shape.
            k_minor (float): An optional minor loss coefficient for including minor losses.

        """
        super(Reach, self).__init__(**kwargs)
        self.invert_1 = invert_1
        self.invert_2 = invert_2
        self.length = length
        self.section = section
        self.k_minor = k_minor

    @property
    def drop(self):
        return self.invert_1 - self.invert_2

    @property
    def long_slope(self):
        return self.drop / self.length

    def velocity(self, depth):
        """Get the velocity of a partial flow section, given a depth from the invert.

        Args:
            depth (float): In :math:`feet`.

        Returns:
            float: Velocity, in :math:`feet/second`.

        """
        r_h = self.section.hyd_radius(depth)
        return constants.K_MANNING * r_h**(2.0/3.0) * self.long_slope**0.5 / self.section.n

    def normal_flow(self, depth):
        """Get the flow of a partial flow section, given a depth from the invert.

        Args:
            depth (float): In :math:`feet`.

        Returns:
            float: Hydraulic flow, in :math:`feet^3/second`.

        """
        a_f = self.section.flow_area(depth)
        vel = self.velocity(depth)
        return a_f * vel

    def froude_number(self, velocity):
        """Get the froude number, used to compare if flow is sub- or super-critical.

        Args:
            velocity (float): In :math:`feet/second`.

        Returns:
            float: A dimensionless number for comparing against critical depth.

        """
        b = math.sqrt(constants.G * self.length)
        return velocity / b

    def shear_stress(self, depth, method='average'):
        """Get the shear stress along the lining of the reach.

        Args:
            depth (float): In :math:`feet`.
            method: The options are `'average'` and `'maximum'`.

        Returns:
            float: : The shear stress, in :math:`pounds/feet^2`.

        """
        if method == 'average':
            b = self.section.hyd_radius(depth)
        elif method == 'maximum':
            b = depth
        else:
            raise ValueError("Either 'average' or 'maximum' must be defined for the method arg.")
        return constants.SG_WATER * b * self.long_slope  # Replace or add option for energy slope

    def critical_depth_accuracy(self, depth, flow):
        """Check solution convergence for critical depth given a trial value.

        Args:
            depth (float): In :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: The difference between the trial and the accurate solution.

        """
        a_f = self.section.flow_area(depth)
        w_s = self.section.surface_width(depth)
        a = w_s * flow**2.0
        b = constants.G * a_f**3.0
        return b - a

    def critical_depth(self, flow):
        """Goal seek a the critical depth in a open flow case.

        Args:
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: the depth where critical flow occurs, in :math:`feet`.

        """
        if self.section.rise:
            bound_upper = self.section.rise
        else:
            bound_upper = None
            for i in range(100):
                depth_trial = i
                if self.critical_depth_accuracy(depth_trial, flow) > 1.0:
                    bound_upper = depth_trial
                    break
        if bound_upper:
            depth = optimize.bisect(
                f=self.critical_depth_accuracy,
                a=1e-12,
                b=bound_upper,
                args=(flow,)
            )
            return float(depth)
        raise Exception('Maximum iterations reached while trying to find an upper bound')

    def critical_velocity(self, flow):
        """Goal seek a the critical velocity in a open flow case.

        Args:
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: the velocity where critical flow occurs, in :math:`feet/second`.

        """
        d_c = self.critical_depth(flow)
        return math.sqrt(constants.G * d_c)

    def critical_slope(self, flow):
        """Goal seek a the critical slope in a open flow case.

        Args:
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: the slope where critical flow occurs, in :math:`feet/feet`.

        """
        d_c = self.critical_depth(flow)
        v_c = self.critical_velocity(flow)
        r_h = self.section.hyd_radius(d_c)
        a = v_c * self.section.n
        b = constants.K_MANNING * r_h**(2.0/3.0)
        return (a / b) ** 2.0

    def friction_slope(self, depth, flow):
        """Get the water surface grade, based on frictional properties.

        Args:
            depth (float): In :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: The slope of the water surface profile, in :math:`feet/feet`.

        """
        a_f = self.section.flow_area(depth)
        vel = flow / a_f
        r_h = self.section.hyd_radius(depth)
        a = vel**2.0 * self.section.n**2.0
        b = constants.K_MANNING**2.0 * r_h**(4.0/3.0)
        return max(a / b, 0.0)

    def friction_loss(self, depth, flow):
        """Get the water surface elevation difference, based on frictional properties.

        Args:
            depth (float): In :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: The difference in elevation, in :math:`feet`.

        """
        return self.length * self.friction_slope(depth, flow)

    def minor_loss(self, depth, flow):
        """Get the water surface elevation difference, based on minor losses.

        Args:
            depth (float): In :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: The difference in elevation, in :math:`feet`.

        """
        if self.k_minor:
            a_f = self.section.flow_area(depth)
            vel = flow / a_f
            return self.k_minor * vel**2.0 / 2.0 / constants.G
        return 0.0

    def section_time(self, depth, flow):
        """Get the travel time of water from end-to-end.

        Args:
            depth (float): In :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: Travel time, in :math:`minutes`.

        """
        a_f = self.section.flow_area(depth)
        vel = flow / a_f
        return self.length / vel / 60.0

    def normal_depth_accuracy(self, depth, flow):
        """Check solution convergence for depth in a open flow case.

        Args:
            depth (float): The assumed value of the depth, in :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: The difference between hydraulic and hydrology flow.

        """
        q_h = self.normal_flow(depth)
        return q_h - flow

    def normal_depth(self, flow):
        """Goal seek a the depth in a open flow case.

        Args:
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: Depth, in :math:`feet`.

        Note:
            The goal is to find a 1:1 ratio of hydraulic to hydrology flow.

        """

        if self.section.rise:
            q_h = self.normal_flow(self.section.rise)
            if flow / q_h > 1.0:
                return self.section.rise
        for i in range(1, 100):
            depth_trial = i
            if self.normal_depth_accuracy(depth_trial, flow) > 1.0:
                depth = optimize.bisect(
                    f=self.normal_depth_accuracy,
                    a=1e-12,
                    b=depth_trial,
                    args=(flow,)
                )
                return float(depth)
        raise Exception('Maximum iterations reached while trying to find an upper bound')

    def velocity_loss(self, depth, flow):
        """Get the vertical head caused by velocity flowing through a reach.

        Args:
            depth (float): The assumed value of the depth, in :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: Elevation difference, in :math:`feet`.

        """
        a_f = self.section.flow_area(depth)
        vel = flow / a_f
        return vel**2.0 / 2.0 / constants.G

    def hgl_2(self, stage_2, flow):
        """Get the hydraulic elevation at the downstream end.

        Args:
            flow (float): Flow, in :math:`feet^3/second`.
            stage_2 (float): The downstream water elevation, in :math:`feet`.

        Returns:
            float: The controlling hydraulic elevation at the downstream end.

        """
        hgl_lower_1 = stage_2
        hgl_lower_2 = self.invert_2 + self.normal_depth(flow)
        return max(hgl_lower_1, hgl_lower_2)

    def hgl_1(self, stage_2, flow):
        """Get the hydraulic elevation at the upstream end.

        Args:
            flow (float): Flow, in :math:`feet^3/second`.
            stage_2 (float): The downstream water elevation, in :math:`feet`.

        Returns:
            float: The controlling hydraulic elevation at the upstream end.

        """
        hgl_lower = self.hgl_2(stage_2, flow)
        hgl_upper_1 = self.invert_1 + self.normal_depth(flow)
        hgl_upper_2 = self.stage_1(hgl_lower, flow)
        return max(hgl_upper_1, hgl_upper_2)

    def energy_1(self, depth, flow):
        """Get the total energy elevation at the upstream end.

        Args:
            depth (float): In :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.

        Returns:
            float: Total upstream energy head.

        """
        y_1 = depth
        h_v = self.velocity_loss(y_1, flow)
        z_1 = self.invert_1
        return z_1 + y_1 + h_v

    def energy_2(self, depth, stage_2, flow):
        """Get the total energy elevation at the downstream end.

        Args:
            depth (float): In :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.
            stage_2 (float): The water elevation at the downstream end, in :math:`feet`.

        Returns:
            float: Total downstream energy head.

        """
        y_2 = stage_2 - self.invert_2
        h_v = self.velocity_loss(y_2, flow)
        z_2 = self.invert_2
        h_f1 = self.friction_loss(depth, flow)
        h_f2 = self.friction_loss(y_2, flow)
        h_f = (h_f1+h_f2) / 2.0
        h_m1 = self.minor_loss(depth, flow)
        h_m2 = self.minor_loss(y_2, flow)
        h_m = (h_m1+h_m2) / 2.0
        return z_2 + y_2 + h_v + h_f + h_m

    def stage_1_accuracy(self, stage_1, stage_2, flow):
        """Check solution convergence for upstream stage_1 elevation.

        Args:
            stage_1 (float): The assumed value of the stage_1 elevation, in :math:`feet`.
            flow (float): Flow, in :math:`feet^3/second`.
            stage_2 (float): The downstream hydraulic elevation, in :math:`feet`.

        Returns:
            float: The difference between energy on each end of the reach.

        """
        depth = stage_1 - self.invert_1
        e_upper = self.energy_1(depth, flow)
        e_lower = self.energy_2(depth, stage_2, flow)
        return e_upper - e_lower

    def stage_1(self, stage_2, flow):
        """Goal seek the depth where energy is balanced between each end of the reach.

        Args:
            flow (float): Flow, in :math:`feet^3/second`.
            stage_2 (float): The downstream hydraulic elevation, in :math:`feet`.

        Returns:
            float: The depth where steady state condition occurs.

        """
        d_lower = stage_2 - self.invert_2
        d_crit = self.critical_depth(flow)
        bound_a = self.invert_1 + 1e-12
        bound_b = self.invert_1 + d_crit
        bound_c = None
        for i in range(1, 100):
            d_trial = i
            if self.section.rise:
                d_trial *= self.section.rise
            hw_trial = self.invert_1 + d_trial
            if self.stage_1_accuracy(hw_trial, stage_2, flow) > 1.0:
                bound_c = hw_trial
                break
        bounds_1 = (bound_a, bound_b) if d_lower < d_crit else (bound_b, bound_c)
        bounds_2 = (bound_b, bound_c) if d_lower < d_crit else (bound_a, bound_b)
        if bound_c:
            try:
                hw = optimize.bisect(
                    f=self.stage_1_accuracy,
                    a=bounds_1[0],
                    b=bounds_1[1],
                    args=(stage_2, flow)
                )
            except ValueError:
                hw = optimize.bisect(
                    f=self.stage_1_accuracy,
                    a=bounds_2[0],
                    b=bounds_2[1],
                    args=(stage_2, flow)
                )
            return float(hw)
        raise Exception('Maximum iterations reached while trying to find an upper bound')

    def flow_accuracy(self, flow, stage_1, stage_2):
        depth = stage_1 - self.invert_1
        e_upper = self.energy_1(depth, flow)
        e_lower = self.energy_2(depth, stage_2, flow)
        return e_upper - e_lower

    def flow(self, stage_1, stage_2):
        # hw = max(stage_1, stage_2)
        # tw = min(stage_1, stage_2)
        for i in range(1, 100):
            d_trial = i
            if self.section.rise:
                d_trial *= self.section.rise
            q_trial = self.normal_flow(d_trial)
            if self.flow_accuracy(q_trial, stage_1, stage_2) > 1.0:
                flow = optimize.bisect(
                    f=self.flow_accuracy,
                    a=1e-12,
                    b=q_trial,
                    args=(stage_1, stage_2)
                )
                return float(flow)
        raise Exception('Maximum iterations reached while trying to find an upper bound')
