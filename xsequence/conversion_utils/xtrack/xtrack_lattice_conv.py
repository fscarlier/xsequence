"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

from xsequence.lattice_baseclasses import Line
import xtrack as xl


def to_xtrack(sliced_line: Line):
    names =  sliced_line.names
    line = [sliced_line[el].to_xtrack() for el in sliced_line]
    xtrack_lattice = xl.Line(elements=line, element_names=names)
    return xtrack_lattice
