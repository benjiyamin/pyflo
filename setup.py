
import os
from distutils.core import setup


def read(filename):
    return open(os.path.join(os.path.dirname(__file__), filename)).read()


setup(
    name='pyflo',
    version=0.1,
    author='benjiyamin, see AUTHORS.rst',
    author_email='benjiyamin@gmail.com',
    description='Hydra is an open-source library written in Python for performing hydraulic and '
                'hydrology stormwater analysis. ',
    license='GNU General Public License, see LICENSE.rst',
    keywords='hydraulics hydrology storm simulation,',
    url='https://github.com/benjiyamin/pyflo',
    packages=['pyflo'],
    long_description=read('README.rst'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python'
    ],
)
