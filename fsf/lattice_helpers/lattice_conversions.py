"""
Module fsf.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import scipy, at, xdeps, math
import fsf.elements as xe
from cpymad.madx import Madx
import xline as xl
from collections import OrderedDict, defaultdict
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


# def from_cpymad(madx: Madx, seq_name: str) -> Tuple[Dict, OrderedDict]:
#     """ Import lattice from cpymad sequence """
#     madx.use(seq_name)
#     
#     sequence_dict = OrderedDict()
#     lat_go = False
#     for elem in madx.sequence[seq_name].elements:
#         elemdata={}
#         for parname, par in elem.cmdpar.items():
#             elemdata[parname]=par.value
#         if 'start' in elem.name:
#             lat_go = True
#         if lat_go:
#             sequence_dict[elem.name] = xe.convert_arbitrary_cpymad_element(elem) 
# 
#     variables=defaultdict(lambda :0)
#     for name,par in madx.globals.cmdpar.items():
#         variables[name]=par.value
# 
#     return variables, sequence_dict 


def from_cpymad(madx: Madx, seq_name: str, dependencies: bool = False) -> Tuple[Dict, OrderedDict]:
    madx.use(seq_name)
    variables=defaultdict(lambda :0)
    for name,par in madx.globals.cmdpar.items():
        variables[name]=par.value

    sequence_dict = OrderedDict()
    elements={}
    for elem in madx.sequence[seq_name].elements:
        elemdata={}
        for parname, par in elem.cmdpar.items():
            elemdata[parname]=par.value
        elements[elem.name]=elemdata
        sequence_dict[elem.name] = xe.convert_arbitrary_cpymad_element(elem) 

    # for el in sequence_dict:
    #     if sequence_dict[el].position_data.reference_element:
    #         sequence_dict[el].position_data.reference = sequence_dict[sequence_dict[el].position_data.reference_element].position_data.position 

    if not dependencies:
        return variables, sequence_dict 

    manager=xdeps.DepManager()
    vref=manager.ref(variables,'variables')
    eref=manager.ref(elements,'elements')
    lref=manager.ref(sequence_dict,'lattice')
    mref=manager.ref(math,'math')
    madeval=xdeps.MadxEval(vref,mref,eref).eval

    for name,par in madx.globals.cmdpar.items():
        if par.expr is not None:
            vref[name]=madeval(par.expr)

    for elem in madx.sequence[seq_name].elements:
        name = elem.name
        for parname, par in elem.cmdpar.items():
            if par.expr is not None:
                if par.dtype==12: # handle lists
                    for ii,ee in enumerate(par.expr):
                        if ee is not None:
                            if parname in ['aper_vx', 'aper_vy']:
                                pass
                            else:
                                eref[name][parname][ii]=madeval(ee)
                else:
                    if parname == 'at':
                        lref[name].position_data.location = madeval(par.expr)
                    elif parname == 'l':
                        lref[name].length = madeval(par.expr)
                    
                    elif parname == 'kmax':
                        try:
                            lref[name].strength_data.kmax = madeval(par.expr)
                        except AttributeError:
                            lref[name].kick_data.kmax = madeval(par.expr)
                    elif parname == 'kmin':
                        try:
                            lref[name].strength_data.kmin = madeval(par.expr)
                        except AttributeError:
                            lref[name].kick_data.kmin = madeval(par.expr)
                    # elif parname == 'calib':
                    #     lref[name]. = madeval(par.expr)
                    elif parname == 'polarity':
                        lref[name].strength_data.polarity = madeval(par.expr)
                    elif parname == 'tilt':
                        lref[name].position_data.tilt = madeval(par.expr)
                    elif parname == 'k0':
                        lref[name].bend_data.k0 = madeval(par.expr)
                    elif parname == 'k1':
                        lref[name].strength_data.k1 = madeval(par.expr)
                    elif parname == 'k1s':
                        lref[name].strength_data.k1s = madeval(par.expr)
                    elif parname == 'k2':
                        lref[name].strength_data.k2 = madeval(par.expr)
                    elif parname == 'k2s':
                        lref[name].strength_data.k2s = madeval(par.expr)
                    elif parname == 'k3':
                        lref[name].strength_data.k3 = madeval(par.expr)
                    elif parname == 'angle':
                        lref[name].bend_data.angle = madeval(par.expr)
                    elif parname == 'kick':
                        lref[name].kick_data.kick = madeval(par.expr)
                    elif parname == 'hkick':
                        lref[name].kick_data.hkick = madeval(par.expr)
                    elif parname == 'vkick':
                        lref[name].kick_data.vkick = madeval(par.expr)
                    elif parname == 'volt':
                        lref[name].rf_data.voltage = madeval(par.expr)
                    elif parname == 'lag':
                        lref[name].rf_data.lag = madeval(par.expr)
                    elif parname == 'slot_id':
                        lref[name].id_data.slot_id = madeval(par.expr)
                    elif parname == 'assembly_id':
                        lref[name].id_data.assembly_id = madeval(par.expr)

    return manager, sequence_dict


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


def to_cpymad(seq_name: str, energy: float, sequence: Sequence) -> Madx:
    madx = Madx()
    madx.option(echo=False, info=False, debug=False)
    seq_command = ''
    
    for name, element in sequence[1:-1].items():
        element.to_cpymad(madx)
        seq_command += f'{name}, at={element.position_data.position}  ;\n'
     
    madx.input(f'{seq_name}: sequence, refer=centre, l={sequence[sequence.names[-1]].position_data.end};')
    madx.input(seq_command)
    madx.input('endsequence;')
    madx.command.beam(particle='electron', energy=energy)
    return madx


def to_pyat(seq_name: str, energy: float, line: Line) -> at.Lattice:
    seq = [line[element].to_pyat() for element in line]
    pyat_lattice = at.Lattice(seq, name=seq_name, key='ring', energy=energy)
    for cav in at.get_elements(pyat_lattice, at.RFCavity):
        cav.Frequency = cav.HarmNumber*scipy.constants.c/pyat_lattice.circumference 
    return pyat_lattice


def to_xline(sliced_line: Line):
    names =  sliced_line.names
    line = [el.to_xline() for el in sliced_line]
    xline_lattice = xl.Line(elements=line, element_names=names)
    return xline_lattice