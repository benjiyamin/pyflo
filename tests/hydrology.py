
import unittest

from pyflo.rational import hydrology, hydraulics
from pyflo import distributions, networks, sections


class RationalEquationTest(unittest.TestCase):
    """From Practice Problems for the Civil Engineering PE Exam by Michael R. Lindeburg, PE:
    Chapter 20

    """

    def test_practice_problem_4(self):
        # Four contiguous 5 ac watersheds are served by an adjacent 1200 ft storm drain (n = 0.013
        # and slope = 0.005). Inlets to the storm drain are placed every 300 ft along the storm
        # drain. The inlet time for each area served by an inlet is 15 min, and the area's runoff
        # coefficient is 0.55. I = 100 / (tc + 10).
        network = networks.Network()
        s201 = network.create_node()
        s202 = network.create_node()
        s203 = network.create_node()
        s204 = network.create_node()
        out = network.create_node()
        rc18 = sections.Circle(diameter=1.5, n=0.012)
        rc24 = sections.Circle(diameter=2.0, n=0.012)
        s201.create_reach(node_2=s202, slope=0.005, section=rc18)
        s202.create_reach(node_2=s203, slope=0.005, section=rc18)
        s203.create_reach(node_2=s204, slope=0.005, section=rc24)
        s204.create_reach(node_2=out, slope=0.005, section=rc18)
        b201 = hydrology.Basin(tc=15.0, area=5.0, c=0.55)
        b202 = hydrology.Basin(tc=15.0, area=5.0, c=0.55)
        b203 = hydrology.Basin(tc=15.0, area=5.0, c=0.55)
        b204 = hydrology.Basin(tc=15.0, area=5.0, c=0.55)
        s201.add_basin(b201)
        s202.add_basin(b202)
        s203.add_basin(b203)
        s204.add_basin(b204)
        i = distributions.Evaluator(
            equation='100.0 / ([t] + 10.0)',
            x_key='[t]',
            x_multi=60.0
        )
        analysis = hydraulics.Analysis(
            node=out,
            tw=6.10,
            intensity=i
        )
        self.data = analysis.hgl_solution_data()
