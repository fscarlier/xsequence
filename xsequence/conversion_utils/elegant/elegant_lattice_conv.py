"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

from pathlib import Path
from typing import Union
from xsequence.lattice_baseclasses import Line


def to_elegant(seq_name: str, energy: float, line: Line, lte_file: Union[str, Path]=None) -> dict:

    elements_definition=""
    # since elegant doesnt support multipoles with different components, 
    # the thinmultipole is split into its different contribution and for each, a MULT element will be added
    # as such, the conversion from the original line would break and line has to be built anew
    element_order=f"{seq_name}: LINE=("
    i=0
    for name, element in line.items():
        name, _, elegant_definition = element.to_elegant()
        elements_definition=f"{elements_definition}{elegant_definition}\n"
        element_order=f"{element_order}{',' if i > 0 else ''}{name}"
        i=i+1
    element_order=f"{element_order})"
    
    if lte_file is not None:
        write_elegant_lattice_file(lte_file, elements_definition, element_order)

    return elements_definition, element_order
    

def write_elegant_lattice_file(filename: Union[str, Path], elements:str, line:str):
    with open(Path(filename).with_suffix('.lte'), 'w') as f:
        f.write(elements)
        f.write('\n')
        f.write(line)

