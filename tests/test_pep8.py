
import os
import unittest

import pep8


class Pep8Test(unittest.TestCase):

    def test_pep8(self):
        style = pep8.StyleGuide()
        style.options.max_line_length = 100
        filenames = []
        for root, _, files in os.walk('./pyflo'):
            python_files = [f for f in files if f.endswith('.py')]
            for file in python_files:
                filename = '{0}/{1}'.format(root, file)
                filenames.append(filename)
        check = style.check_files(filenames)
        self.assertEqual(check.total_errors, 0, 'PEP8 style errors: %d' % check.total_errors)
