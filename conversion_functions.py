import os, sys
import copy
from cpymad.madx import Madx
import at
import elements
import lattice

CPYMAD_TO_FFF_MAP = {'marker': elements.Marker, 
                     'drift':  elements.Drift, 
                     'rbend':  elements.Rbend, 
                     'sbend':  elements.Sbend, 
                     'quadrupole': elements.Quadrupole, 
                     'sextupole': elements.Sextupole, 
                     'rfcavity': elements.RFCavity}


def create_cpymad_from_file(sequence_path, energy, particle_type='electron', logging=False):
    if logging:
        madx = Madx(command_log='log.madx')
    else:
        madx = Madx()
    madx.call(file=sequence_path)
    madx.input('SET, FORMAT="25.20e";')
    madx.command.beam(particle=particle_type, energy=energy)
    return madx


def create_global_elements_from_cpymad(madx):
    idx = 0
    global_elements = []
    while '$start' not in madx.elements[idx].name:
        if madx.elements[idx].name not in madx.base_types:
            gl_ele = convert_cpymad_element(madx.elements[idx])
            global_elements.append(gl_ele)
        idx += 1
    return global_elements


def import_lattice_from_cpymad(madx):
    global_elements = create_global_elements_from_cpymad(madx)
    sequences = []

    for seq_name in madx.sequence:
        madx.use(seq_name)
        total_length = madx.sequence[seq_name].elements[-1].at
        seq = madx.sequence[seq_name].elements
        element_seq = list(map(convert_cpymad_element, seq))
        sequence = lattice.Lattice(seq_name, element_seq, key='sequence', 
                                   energy=madx.sequence[seq_name].beam.energy, 
                                   global_elements=global_elements)
        sequences.append(sequence)
    if len(sequences) == 1:
        return sequences[0]
    else:
        return sequences


def create_cpymad_from_lattice(lattice):
    global_elements = lattice.global_elements
    elements = lattice._sequence

    
    madx = Madx(command_log='log.madx')
    seq_command = ''
    for element in global_elements:
        element_type = element.__class__.__name__.lower()
        kwargs = copy.copy(vars(element))
        kwargs['l'] = kwargs.pop('length')
        kwargs['at'] = kwargs.pop('pos')
        
        # Should develop complete constraint on allowed keyword arguments for cpymad
        kwargs.pop('name')
        kwargs.pop('parent')
        if 'arc_length' in kwargs.keys():
            kwargs.pop('arc_length')
        
        madx.command[element_type].clone(element.name, **kwargs)
    
    for element in elements[1:-1]:
        element_type = element.__class__.__name__.lower()
        kwargs = copy.copy(vars(element))
        kwargs['l'] = kwargs.pop('length')
        kwargs['at'] = kwargs.pop('pos')
        
        # Should develop complete constraint on allowed keyword arguments for cpymad
        kwargs.pop('name')
        kwargs.pop('parent')
        if 'arc_length' in kwargs.keys():
            kwargs.pop('arc_length')
        
        madx.command[element_type].clone(element.name, **kwargs)
        seq_command += f'{element.name}, at={element.pos}  ;\n'
    madx.input(f'{lattice.name}: sequence, refer=centre, l={lattice._sequence[-1].pos};')
    madx.input(seq_command)
    madx.input('endsequence;')
    madx.command.beam(particle='electron', energy=lattice.energy)
    return madx


def convert_cpymad_element(ele):
    name = ele.name.replace('.', '_').lower()
    kw_dict = dict(ele.items())
    kw_dict['pos'] = kw_dict.pop('at')
    kw_dict['length'] = kw_dict.pop('l')
    kw_dict['parent'] = ele.parent.name
    base_type = ele.base_type.name
    return CPYMAD_TO_FFF_MAP[base_type](name, **kw_dict)


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
