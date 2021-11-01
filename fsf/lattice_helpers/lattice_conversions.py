"""
Module fsf.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import scipy, at
import fsf.elements as xe
from cpymad.madx import Madx
import xline as xl
from collections import defaultdict
from typing import List, Tuple, Dict
from fsf.lattice_baseclasses import Sequence, Line


def from_madx_seqfile(seq_file, energy: float, particle_type: str = 'electron') -> Madx:
    """ Import lattice from MAD-X sequence file """
    madx = Madx()
    madx.option(echo=False, info=False, debug=False)
    madx.call(file=seq_file)
    madx.input('SET, FORMAT="25.20e";')
    madx.command.beam(particle=particle_type, energy=energy)
    return madx


def from_cpymad(madx: Madx, seq_name: str) -> Tuple(Dict, List):
    """ Import lattice from cpymad sequence """
    madx.use(seq_name)
    element_seq = list(map(xe.convert_arbitrary_cpymad_element, 
                            madx.sequence[seq_name].elements))
    
    variables=defaultdict(lambda :0)
    for name,par in madx.globals.cmdpar.items():
        variables[name]=par.value
    return variables, element_seq 


def from_pyat(pyat_lattice: at.Lattice) -> List[xe.BaseElement]:
    seq = []
    for el in pyat_lattice:
        new_element = xe.convert_arbitrary_pyat_element(el)
        seq.append(new_element)
    return seq 


def to_cpymad(seq_name: str, sequence: Sequence) -> Madx:
    madx = Madx()
    madx.option(echo=False, info=False, debug=False)
    seq_command = ''
    
    elements = sequence
    for element in elements[1:-1]:
        element.to_cpymad(madx)
        seq_command += f'{element.name}, at={element.position_data.position}  ;\n'
    
    madx.input(f'{seq_name}: sequence, refer=centre, l={sequence[-1].position_data.end};')
    madx.input(seq_command)
    madx.input('endsequence;')
    madx.command.beam(particle='electron', energy=self.params['energy'])
    return madx


def to_pyat(seq_name: str, energy: float, line: Line) -> at.Lattice:
    seq = [element.to_pyat() for element in line]
    pyat_lattice = at.Lattice(seq, name=seq_name, key='ring', energy=energy)
    for cav in at.get_elements(pyat_lattice, at.RFCavity):
        cav.Frequency = cav.HarmNumber*scipy.constants.c/pyat_lattice.circumference 
    return pyat_lattice


def to_xline(sliced_line: Line):
    names =  sliced_line.names
    line = [el.to_xline() for el in sliced_line]
    xline_lattice = xl.Line(elements=line, element_names=names)
    return xline_lattice