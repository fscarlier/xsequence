"""
Module fsf.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import at
import scipy
import fsf.elements as xe
from collections import OrderedDict
from fsf.lattice_baseclasses import Line


def from_pyat(pyat_lattice: at.Lattice) -> OrderedDict:
    seq = OrderedDict()
    for el in pyat_lattice:
        name = el.FamName
        if name in seq.keys():
            n = 1
            while f"{name}_{n}" in seq.keys():
                n += 1
            name = f"{name}_{n}"
        seq[name] = xe.convert_arbitrary_pyat_element(el)
    return seq 


def to_pyat(seq_name: str, energy: float, line: Line) -> at.Lattice:
    
    seq = [line[element].to_pyat() for element in line]
    pyat_lattice = at.Lattice(seq, name=seq_name, key='ring', energy=energy)
    for cav in at.get_elements(pyat_lattice, at.RFCavity):
        cav.Frequency = cav.HarmNumber*scipy.constants.c/pyat_lattice.circumference 
    return pyat_lattice


