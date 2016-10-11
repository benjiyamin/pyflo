
import json
import unittest

from pyflo import sections, networks, distributions
from pyflo.rational import hydraulics, hydrology


class ImportIntensityFromJsonTest(unittest.TestCase):

    def setUp(self):
        with open('./resources/intensity/fdot.json') as data_file:
            self.data = json.load(data_file)

    def test_intensty_equation(self):
        data = self.data['equation']
        control = '[a] + [b] * log([t]) + [c] * log([t])**2 + [d] * log([t])**3'
        self.assertEqual(data, control)

    def test_intensity_x_key(self):
        data = self.data['input_key']
        control = '[t]'
        self.assertEqual(data, control)

    def test_intensity_coefficients(self):
        zone10_data = [zone for zone in self.data['zones'] if zone['name'] == 'FDOT ZONE 10'][0]
        year03_data = [freq for freq in zone10_data['frequencies'] if freq['duration'] == 3][0]
        data = year03_data['coefficients']
        control = {'[a]': 11.32916, '[b]': -1.38557, '[c]': -0.36672, '[d]': 0.05012}
        self.assertEqual(data, control)


class OneReachGeopakTest(unittest.TestCase):

    def setUp(self):
        network = networks.Network()
        s31 = network.create_node()
        out = network.create_node()
        rc18 = sections.Circle(diameter=1.5, n=0.012)
        s31.create_reach(node_2=out, invert_1=4.1, invert_2=4.0, length=65.76, section=rc18)
        b31 = hydrology.Basin(tc=10.0, area=1.58, c=0.276)
        s31.add_basin(b31)
        zone10_03year = distributions.Evaluator(
            equation='[a] + [b] * log([t]) + [c] * log([t])**2 + [d] * log([t])**3',
            x_key='[t]',
            eq_kwargs={'[a]': 11.32916, '[b]': -1.38557, '[c]': -0.36672, '[d]': 0.05012},
            x_multi=60.0
        )
        analysis = hydraulics.Analysis(
            node=out,
            tw=4.85,
            intensity=zone10_03year
        )
        self.node = out
        self.data = analysis.hgl_solution_data()

    def test_get_cumulative_runoff(self):
        data = tuple([round(l['runoff_area'], 1) for l in hydraulics.totaled_basin_data(self.node)])
        control = (round(0.276 * 1.58, 1),)
        self.assertTupleEqual(data, control)

    def test_flow(self):
        data = tuple([round(line['flow'], 1) for line in self.data])
        control = (3.0,)
        self.assertTupleEqual(data, control)

    def test_hgl_upper(self):
        data = tuple([round(line['hgl_upper'], 1) for line in self.data])
        control = (5.0,)
        self.assertTupleEqual(data, control)

    def test_hgl_lower(self):
        data = tuple([round(line['hgl_lower'], 1) for line in self.data])
        control = (4.9,)
        self.assertTupleEqual(data, control)


class FiveReachGeopakTest(unittest.TestCase):

    def setUp(self):
        network = networks.Network()
        s201 = network.create_node()
        s202 = network.create_node()
        s203 = network.create_node()
        s204 = network.create_node()
        s203a = network.create_node()
        out = network.create_node()
        rc18 = sections.Circle(diameter=1.5, n=0.012)
        rc24 = sections.Circle(diameter=2.0, n=0.012)
        s201.create_reach(node_2=s203, invert_1=25.5, invert_2=20.3, length=642.35, section=rc18)
        s202.create_reach(node_2=s204, invert_1=25.4, invert_2=20.3, length=625.32, section=rc18)
        s203.create_reach(node_2=s203a, invert_1=-1.0, invert_2=-1.2, length=85.82, section=rc24)
        s204.create_reach(node_2=s203, invert_1=19.5, invert_2=19.3, length=81.26, section=rc18)
        s203a.create_reach(node_2=out, invert_1=-1.2, invert_2=-1.3, length=23.00, section=rc24)
        b201 = hydrology.Basin(tc=10.0, area=1.00, c=0.950)
        b202 = hydrology.Basin(tc=10.0, area=0.99, c=0.950)
        b203 = hydrology.Basin(tc=10.0, area=0.71, c=0.950)
        b204 = hydrology.Basin(tc=10.0, area=0.70, c=0.950)
        s201.add_basin(b201)
        s202.add_basin(b202)
        s203.add_basin(b203)
        s204.add_basin(b204)
        zone10_03year = distributions.Evaluator(
            equation='[a] + [b] * log([t]) + [c] * log([t])**2 + [d] * log([t])**3',
            x_key='[t]',
            eq_kwargs={'[a]': 11.32916, '[b]': -1.38557, '[c]': -0.36672, '[d]': 0.05012},
            x_multi=60.0
        )
        analysis = hydraulics.Analysis(
            node=out,
            tw=6.10,
            intensity=zone10_03year
        )
        self.node = out
        self.data = analysis.hgl_solution_data()

    def test_get_cumulative_runoff(self):
        data = tuple([round(l['runoff_area'], 2) for l in hydraulics.totaled_basin_data(self.node)])
        control = (0.94, 1.61, 0.95, 3.23, 3.23)
        self.assertTupleEqual(data, control)

    def test_flow(self):
        data = tuple([round(line['flow'], 1) for line in self.data])
        control = (6.5, 10.4, 6.5, 20.9, 20.7)
        self.assertTupleEqual(data, control)

    def test_hgl_upper(self):
        data = tuple([round(line['hgl_upper'], 1) for line in self.data])
        control = (26.3, 21.5, 26.4, 6.9, 6.3)
        self.assertTupleEqual(data, control)

    def test_hgl_lower(self):
        data = tuple([round(line['hgl_lower'], 1) for line in self.data])
        control = (21.5, 20.8, 21.2, 6.3, 6.1)
        self.assertTupleEqual(data, control)


class FlatAnalysisTest(unittest.TestCase):

    def setUp(self):
        network = networks.Network()
        s1 = network.create_node()
        s2 = network.create_node()
        s3 = network.create_node()
        s4 = network.create_node()
        s5 = network.create_node()
        s6 = network.create_node()
        s7 = network.create_node()
        s8 = network.create_node()
        ol = network.create_node()
        rc18 = sections.Circle(diameter=1.5, n=0.012)
        rc24 = sections.Circle(diameter=2.0, n=0.012)

        s1.create_reach(node_2=s2, invert_1=6.4, invert_2=6.2, length=110.0, section=rc18)
        s2.create_reach(node_2=s3, invert_1=6.2, invert_2=5.9, length=200.0, section=rc18)
        s3.create_reach(node_2=s4, invert_1=5.9, invert_2=5.6, length=200.0, section=rc18)
        s4.create_reach(node_2=s7, invert_1=5.6, invert_2=5.4, length=100.0, section=rc18)
        s5.create_reach(node_2=s7, invert_1=5.6, invert_2=5.4, length=110.0, section=rc18)
        s7.create_reach(node_2=s8, invert_1=5.4, invert_2=4.5, length=025.0, section=rc24)
        s6.create_reach(node_2=s8, invert_1=4.6, invert_2=4.5, length=032.0, section=rc18)
        s8.create_reach(node_2=ol, invert_1=4.5, invert_2=4.2, length=250.0, section=rc24)

        b1 = hydrology.Basin(tc=10.0, shapes=((0.30, 0.95), (0.05, 0.20)))
        s1.add_basin(b1)

        b2 = hydrology.Basin(tc=10.0, shapes=((0.20, 0.95), (0.03, 0.20)))
        s2.add_basin(b2)

        b4 = hydrology.Basin(tc=10.0, shapes=((0.40, 0.95), (0.10, 0.20)))
        s4.add_basin(b4)

        b5 = hydrology.Basin(tc=10.0, shapes=((0.40, 0.95), (0.50, 0.20)))
        s5.add_basin(b5)

        b6 = hydrology.Basin(tc=10.0, shapes=((0.15, 0.95), (0.50, 0.20)))
        s6.add_basin(b6)

        b8 = hydrology.Basin(tc=10.0, shapes=((0.25, 0.95), (0.50, 0.20)))
        s8.add_basin(b8)

        zone06_03year = distributions.Evaluator(
            equation='[a] + [b] * log([t]) + [c] * log([t])**2 + [d] * log([t])**3',
            x_key='[t]',
            eq_kwargs={'[a]': 14.98331, '[b]': -4.44963, '[c]': 0.35683, '[d]': -0.00224},
            x_multi=60.0
        )

        analysis = hydraulics.Analysis(
            node=ol,
            tw=8.3,
            intensity=zone06_03year
        )

        self.node = ol
        self.data = analysis.hgl_solution_data()

    def test_get_cumulative_runoff(self):
        data = tuple([round(l['runoff_area'], 1) for l in hydraulics.totaled_basin_data(self.node)])
        control = (0.5, 0.3, 0.5, 0.5, 0.9, 1.4, 0.2, 2.0)
        self.assertTupleEqual(data, control)

    def test_physical_fall(self):
        data = tuple([round(l['reach'].invert_1 - l['reach'].invert_2, 1) for l in self.data])
        control = (0.2, 0.2, 0.3, 0.3, 0.2, 0.9, 0.1, 0.3)
        self.assertTupleEqual(data, control)


class SteepAnalysisTest(unittest.TestCase):

    def setUp(self):
        network = networks.Network()
        s11 = network.create_node()
        s12 = network.create_node()
        s13 = network.create_node()
        s14 = network.create_node()
        s15 = network.create_node()
        out = network.create_node()
        rc18 = sections.Circle(diameter=1.5, n=0.012)
        rc24 = sections.Circle(diameter=2.0, n=0.012)

        s15.create_reach(node_2=s14, invert_1=55.2, invert_2=54.7, length=300.0, section=rc18)
        s14.create_reach(node_2=s13, invert_1=54.7, invert_2=54.2, length=300.0, section=rc18)
        s13.create_reach(node_2=s12, invert_1=54.2, invert_2=50.0, length=300.0, section=rc18)
        s12.create_reach(node_2=s11, invert_1=50.0, invert_2=46.0, length=300.0, section=rc18)
        s11.create_reach(node_2=out, invert_1=45.5, invert_2=44.5, length=300.0, section=rc24)

        b15 = hydrology.Basin(tc=10.0, area=0.2, c=0.80)
        s15.add_basin(b15)

        b14 = hydrology.Basin(tc=10.0, area=1.0, c=0.80)
        s14.add_basin(b14)

        b13 = hydrology.Basin(tc=10.0, area=0.6, c=0.80)
        s13.add_basin(b13)

        b12 = hydrology.Basin(tc=10.0, area=0.5, c=0.80)
        s12.add_basin(b12)

        b11 = hydrology.Basin(tc=10.0, area=1.1, c=0.80)
        s11.add_basin(b11)

        zone07_03year = distributions.Evaluator(
            equation='[a] + [b] * log([t]) + [c] * log([t])**2 + [d] * log([t])**3',
            x_key='[t]',
            eq_kwargs={'[a]': 12.43560, '[b]': -2.56458, '[c]': -0.06903, '[d]': 0.02787},
            x_multi=60.0
        )

        analysis = hydraulics.Analysis(
            node=out,
            tw=47.1,
            intensity=zone07_03year
        )

        self.node = out
        self.data = analysis.hgl_solution_data()

    def test_get_cumulative_runoff(self):
        data = tuple([round(l['runoff_area'], 2) for l in hydraulics.totaled_basin_data(self.node)])
        control = (0.16, 0.96, 1.44, 1.84, 2.72)
        self.assertTupleEqual(data, control)

    def test_flow(self):
        data = tuple([round(line['flow'], 1) for line in self.data])
        control = (1.0, 5.8, 8.3, 10.4, 15.1)
        self.assertTupleEqual(data, control)

    def test_physical_fall(self):
        data = tuple([round(l['reach'].invert_1 - l['reach'].invert_2, 2) for l in self.data])
        control = (0.5, 0.5, 4.2, 4.0, 1.0)
        self.assertTupleEqual(data, control)
