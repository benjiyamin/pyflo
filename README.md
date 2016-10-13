# Project PyFlo

PyFlo is an open-source library written in Python for performing
hydraulic and hydrology stormwater analysis. Capabilities include
network hydraulic grade analysis and time/iteration based storage and flood
routing simulations. SCS Unit Hydrograph and Rational Method are included
for basin computations. Most of the calculations and procedures are
derived from available existing publications and resources. There are
some GUI programs available that have similar capabilities. The intent is
that many will build from and contribute to the project, making it much
more powerful than a single person ever could.

## Installation

Installing the easy way, using pip:

```bash
$ pip install pyflo
```

Setting up a clean working environment, using virtualenv:

```bash
$ virtualenv -p python3 venv
$ source venv/bin/activate
$ pip install -r requirements.txt
```

## Examples

### Runoff Hydrograph

From [NEH Hydrology Ch. 16, Ex. 16-1](http://www.wcc.nrcs.usda.gov/ftpref/wntsc/H&H/NEHhydrology/ch16.pdf#page=15):

```python
from pyflo import system, distributions
from pyflo.nrcs import hydrology

runoff_dist = system.tuple_list_from_csv('./resources/distributions/runoff/scs484.csv')
uh484 = distributions.Distribution(runoff_dist)
basin = hydrology.Basin(
    area=4.6,
    cn=85.0,
    tc=2.3,
    runoff_dist=uh484,
    peak_factor=484.0
)

runoff_hydrograph = basin.runoff_hydrograph(x_step=0.1)

```

## Contributing

For developers, it's important to use common best practices when contributing to the project.
[PEP 8](https://www.python.org/dev/peps/pep-0008/) should always be adhered to. Code should be
documented with [Google style docstrings](http://sphinxcontrib-napoleon.readthedocs.io/en/latest/example_google.html
Pull requests and filing issues are encouraged. We'd love to hear what works for you, and what 
does not.

To get started with contributing with the PyFlo repository:

1. Fork it!
2. Create your feature branch: `git checkout -b my-new-feature`
3. Commit your changes: `git commit -am 'Add some feature'`
4. Push to the branch: `git push origin my-new-feature`
5. Submit a pull request :D

For a list of  contributors who have participated in this project,
check out [AUTHORS.md](AUTHORS.md).

## Testing

Unit Testing is currently done using the built-in unittest module:

```bash
$ python tests.py
```

## License

This project is licensed under GPL 2.0 - see [LICENSE.md](LICENSE.md) for details.