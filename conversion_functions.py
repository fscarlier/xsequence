import os, sys
import time
import numpy as np
from cpymad.madx import Madx
import at
import elements
import lattice

    

def convert_marker(ele):
    marker = elements.Marker(ele.name.replace('.', '_').lower(), pos=ele.at)
    return marker


def convert_drift(ele):
    drift = elements.Drift(ele.name.replace('.', '_').lower(), length=ele.l, pos=ele.at)
    return drift


def convert_sbend(ele):
    dipole = elements.Dipole(ele.name.replace('.', '_').lower(), length=ele.l, angle=ele.angle, pos=ele.at)
    return dipole


def convert_rbend(ele):
    dipole = elements.Dipole(ele.name.replace('.', '_').lower(), chord_length=ele.l, angle=ele.angle, pos=ele.at, bend_type='rbend', e1=ele.e1, e2=ele.e2)
    return dipole


def convert_quadrupole(ele):
    quad = elements.Quadrupole(ele.name.replace('.', '_').lower(), length=ele.l, knl=[0.0,ele.k1], ksl=[0.0,ele.k1s], pos=ele.at)
    return quad


def convert_sextupole(ele):
    sext = elements.Sextupole(ele.name.replace('.', '_').lower(), length=ele.l, knl=[0.0,0.0,ele.k2], ksl=[0.0,0.0,ele.k2s], pos=ele.at)
    return sext


def convert_rfcavity(ele):
    rfcavity = elements.RFCavity(ele.name.replace('.', '_').lower(), length=ele.l, volt=ele.volt, freq=ele.freq*1e6, pos=ele.at)
    return rfcavity


def create_cpymad_from_file(sequence_path, energy):
    madx = Madx(command_log='loginp.madx')
    madx.call(file=sequence_path)
    # madx.input('SET, FORMAT="25.20e";')
    madx.command.beam(particle='electron', energy=energy)
    return madx


def import_lattice_from_cpymad(madx):
    idx = 0
    while '$start' not in madx.elements[idx].name:
        if madx.elements[idx].name not in madx.base_types:
            create_new_type(madx.elements[idx])
        idx += 1

    for seq_name in madx.sequence:
        madx.use(seq_name)
        total_length = madx.sequence[seq_name].elements[-1].at
        seq = madx.sequence[seq_name].elements
        element_seq = list(map(convert_cpymad_element, seq))
        sequence = lattice.Lattice(seq_name, element_seq, key='sequence', energy=madx.sequence[seq_name].beam.energy)
    return sequence


def create_pyat_from_lattice(lattice):
    elements = lattice._sequence_with_drifts
    seq = []
    for element in elements:
        if element.__class__.__name__ == 'Dipole':
            dipole = at.lattice.elements.Dipole(element.name, element.length, 
                                       angle=element.angle, EntranceAngle=element.e1, 
                                       ExitAngle=element.e2)
            seq.append(dipole)
        if element.__class__.__name__ == 'Drift':
            drift = at.lattice.elements.Drift(element.name, element.length)
            seq.append(drift)
        elif element.__class__.__name__ == 'Quadrupole':
            quadrupole = at.lattice.elements.Quadrupole(element.name, element.length, 
                                           k1=element.knl[1], k1s=element.ksl[1])
            seq.append(quadrupole)
        elif element.__class__.__name__ == 'Sextupole':
            sextupole = at.lattice.elements.Sextupole(element.name, element.length, 
                                          k2=element.knl[2], k2s=element.ksl[2])
            seq.append(sextupole)
        elif element.__class__.__name__ == 'Marker':
            marker = at.lattice.elements.Marker(element.name)
            seq.append(marker)
        elif element.__class__.__name__ == 'RFCavity':
            harmonic_number = int(element.freq/(3e8/elements[-1].pos))
            rfcavity = at.lattice.elements.RFCavity(element.name.replace('.', '_').upper(), 
                                                    element.length, voltage=element.volt, frequency=element.freq, 
                                                    harmonic_number=harmonic_number, 
                                                    energy=lattice.energy)
            seq.append(rfcavity)
    pyat_lattice = at.Lattice(seq, key=lattice.name, energy=lattice.energy*1e9)
    return pyat_lattice


def create_cpymad_from_lattice(lattice):
    elements = lattice._sequence
    madx = Madx(command_log='log.madx')
    seq_command = ''
    for element in elements[1:-1]:
        if element.__class__.__name__ == 'Dipole':
            if element.bend_type == 'sbend':
                madx.command.sbend.clone(element.name, l=element.length, angle=element.angle)
            elif element.bend_type == 'rbend':
                madx.command.rbend.clone(element.name, l=element.chord_length, angle=element.angle, e1=element.e1, e2=element.e2)
        elif element.__class__.__name__ == 'Quadrupole':
            madx.command.quadrupole.clone(element.name, l=element.length, k1=element.knl[1], k1s=element.ksl[1])
        elif element.__class__.__name__ == 'Sextupole':
            madx.command.sextupole.clone(element.name, l=element.length, k2=element.knl[2], k2s=element.ksl[2])
        elif element.__class__.__name__ == 'Marker':
            madx.command.marker.clone(element.name)
        elif element.__class__.__name__ == 'RFCavity':
            madx.command.rfcavity.clone(element.name, l=element.length, volt=element.volt, freq=element.freq*1e-6)
        seq_command += f'{element.name}, at={element.pos}  ;\n'
    madx.input(f'{lattice.name}: sequence, refer=centre, l={lattice._sequence[-1].pos};')
    madx.input(seq_command)
    madx.input('endsequence;')
    madx.command.beam(particle='electron', energy=lattice.energy)
    return madx


def convert_cpymad_element(ele):
    return CPYMAD_TO_LATTICE_CONVERT_MAP[ele.base_type.name](ele)



LATTICE_TO_CPYMAD_CONVERT_MAP = {'marker': convert_marker, 
                                 'drift': convert_drift, 
                                 'rbend': convert_rbend, 
                                 'sbend': convert_sbend, 
                                 'quadrupole': convert_quadrupole, 
                                 'sextupole': convert_sextupole, 
                                 'rfcavity': convert_rfcavity}


CPYMAD_TO_LATTICE_CONVERT_MAP = {'marker': convert_marker, 
                                 'drift': convert_drift, 
                                 'rbend': convert_rbend, 
                                 'sbend': convert_sbend, 
                                 'quadrupole': convert_quadrupole, 
                                 'sextupole': convert_sextupole, 
                                 'rfcavity': convert_rfcavity}













