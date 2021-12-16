"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

from xsequence.lattice_baseclasses import Line
import xline as xl


def to_xline(sliced_line: Line):
    names =  sliced_line.names
    line = [sliced_line[el].to_xline() for el in sliced_line]
    xline_lattice = xl.Line(elements=line, element_names=names)
    return xline_lattice
