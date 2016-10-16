"""Functions for executing system commands.

:copyright: 2016, See AUTHORS for more details.
:license: GNU General Public License, See LICENSE for more details.

"""

import csv
import os
from typing import List, Tuple

import numpy


def tuple_list_from_csv(filename):
    """Open a csv file and get a list of tuples that represents the data.

    Args:
        filename (str): The name of the file to open.

    Returns:
        List[Tuple[float, float]]: Each row of data is a list item. The columns of data in the row
            are represented by a tuple.

    Raises:
        IOError: if the specified filename does not have an associated file.

    """
    if os.path.isfile(filename):
        open_file = open(filename, "rt")
        reader = csv.reader(open_file, delimiter=',')
        tuple_list = []
        for row in reader:
            tuple_new = tuple((float(col) for col in row))
            tuple_list.append(tuple_new)
        open_file.close()
        return tuple_list
    raise IOError


def array_from_csv(filename):
    """Open a csv file and get a numpy array that represents the data.

    Args:
        filename (str): The name of the file to open.

    Returns:
        numpy.ndarray: a numpy array representing the data.

    """
    data = tuple_list_from_csv(filename)
    array = numpy.array(data)
    return array


def csv_from_tuple_list(filename, data):
    """Write a list of tuples that represents data to a csv file.

    Args:
        filename (str): The name of the file to write data.
        data (List[Tuple[float, float]]): Each item in the list that will be written to each row of
            the file.

    """
    with open(filename, 'w') as out:
        csv_out = csv.writer(out)
        for row in data:
            csv_out.writerow(row)
