# foamPy
[![Stories in Ready](https://badge.waffle.io/petebachant/foampy.png?label=ready&title=Ready)](https://waffle.io/petebachant/foampy)

A work-in-progress Python package for working with OpenFOAM--not to be confused
with PyFoam. Basically, this is a collection of useful functions and scripts
I have written and want to have available for the sake of reproducibility.


## Installation

### With `pip`

    pip install foampy


### From source

Clone this repository, and in this directory run

    python setup.py install


## Usage

### Assessing the progress of an OpenFOAM run

In a case directory, run

    foampy-progress

For a PyQt GUI progress bar run

    foampy-progress-gui


## Development

To run tests, execute

    py.test
