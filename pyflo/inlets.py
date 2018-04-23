
from pyflo.distributions import Evaluator


class Inlet(object):

    def __init__(self, eff_eval):
        self.eff_eval = eff_eval

    def efficiency(self, flow):
        pass
