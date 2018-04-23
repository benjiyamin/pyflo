
import unittest

from scipy import interpolate, optimize


def goal_seek(function, bounds, goal, max_iterations, tolerance, func_args=None):
    a, b = bounds
    if func_args:
        solve_a = function(a, *func_args)
        solve_b = function(b, *func_args)
    else:
        solve_a = function(a)
        solve_b = function(b)
    if min(solve_a, solve_b) < goal < max(solve_a, solve_b):
        for i in range(max_iterations):
            c = (a + b) / 2.0
            if func_args:
                solve_a = function(a, *func_args)
                solve_c = function(c, *func_args)
            else:
                solve_a = function(a)
                solve_c = function(c)
            y_a = (solve_a / goal) - 1.0
            y_c = (solve_c / goal) - 1.0
            if abs(b - a) / 2.0 < tolerance:  # Solution Found
                return c
            elif y_a * y_c < 0.0:
                b = c
            else:
                a = c  # New Interval
        raise Exception('Maximum iterations reached while trying to find a solution')
    raise ValueError('One bound has to cause a solution to be too low, the other too high.')


class MathsTest(unittest.TestCase):

    def test_goal_seek(self):

        def solve_poly(x):
            y = pow(x, 4) - 10 * pow(x, 3) + 35 * pow(x, 2) - 50 * x + 24
            return y

        expected = 1234.2
        out = solve_poly(expected)

        produced = goal_seek(
            function=solve_poly,
            bounds=(0, 10000),
            goal=out,
            max_iterations=100,
            tolerance=1e-12
        )

        self.assertAlmostEqual(produced, expected, 4)

    def test_scipy_goal_seek(self):

        def solve_poly_old(x):
            y = pow(x, 4) - 10 * pow(x, 3) + 35 * pow(x, 2) - 50 * x + 24
            return y

        def solve_poly_new(x, goal):
            y = pow(x, 4) - 10 * pow(x, 3) + 35 * pow(x, 2) - 50 * x + 24 - goal
            return y

        control_in = 1234.2
        out = solve_poly_old(control_in)

        expected = goal_seek(
            function=solve_poly_old,
            bounds=(0, 10000),
            goal=out,
            max_iterations=100,
            tolerance=1e-12
        )

        produced = optimize.bisect(
            f=solve_poly_new,
            a=0,
            b=10000,
            args=(out,)
        )

        self.assertAlmostEqual(produced, expected, 4)

    def test_numpy_interpolation(self):
        table = (
            (0.1, 25.0),
            (0.2, 30.0),
            (0.3, 10.0),
            (0.4, 70.0),
            (0.5, 05.0),
            (0.6, 30.0),
            (0.7, 25.0),
            (0.8, 70.0),
            (0.9, 10.0),
            (1.0, 99.0),
        )
        value = .35
        x = [row[0] for row in table]
        y = [row[1] for row in table]
        y_interp = interpolate.interp1d(x, y)
        produced = y_interp(value)
        expected = (10.0 + 70.0) / 2.0
        self.assertAlmostEqual(produced, expected)
