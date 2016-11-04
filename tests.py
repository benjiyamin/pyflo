
import unittest
import sys


if __name__ == '__main__':
    testsuite = unittest.TestLoader().discover('tests')
    ret = int(not unittest.TextTestRunner(verbosity=2).run(testsuite).wasSuccessful())
    sys.exit(ret)
