import os, sys
import copy
import scipy
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


PYAT_TO_FFF_MAP = {'Marker': elements.Marker, 
                   'Drift':  elements.Drift, 
                   'Dipole':  elements.Sbend, 
                   'Quadrupole': elements.Quadrupole, 
                   'Sextupole': elements.Sextupole, 
                   'RFCavity': elements.RFCavity}


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
            gl_ele = convert_cpymad_element_to_fff(madx.elements[idx])
            global_elements.append(gl_ele)
        idx += 1
    return global_elements


def import_lattice_from_cpymad(madx):
    global_elements = create_global_elements_from_cpymad(madx)
    sequences = []

    for seq_name in madx.sequence:
        madx.use(seq_name)
        total_length = madx.sequence[seq_name].elements[-1].at
        element_seq = list(map(convert_cpymad_element_to_fff, madx.sequence[seq_name].elements))
        sequence = lattice.Lattice(seq_name, element_seq, key='sequence', 
                                   energy=madx.sequence[seq_name].beam.energy, 
                                   global_elements=global_elements)
        sequences.append(sequence)
    if len(sequences) == 1:
        return sequences[0]
    else:
        return sequences


def export_cpymad_from_lattice(lattice):
    # TODO: - Should develop complete constraint on allowed keyword arguments for cpymad
    #       - Reproduce inheritance from global elements
    madx = Madx(command_log='log.madx')
    seq_command = ''
    global_elements_defined = False
    
    try: 
        global_elements = lattice.global_elements
        for element in global_elements:
            convert_fff_element_to_cpymad(element, madx)
        global_elements_defined = True
    except AttributeError:
        print("No global elements in cpymad instance")

    elements = lattice._sequence
    for element in elements[1:-1]:
        if not global_elements_defined:
            convert_fff_element_to_cpymad(element, madx)
            seq_command += f'{element.name}, at={element.pos}  ;\n'
        else:
            seq_command += f'{element.name}: {element.parent}, at={element.pos}  ;\n'
    
    madx.input(f'{lattice.name}: sequence, refer=centre, l={lattice._sequence[-1].pos};')
    madx.input(seq_command)
    madx.input('endsequence;')
    madx.command.beam(particle='electron', energy=lattice.energy)
    return madx


def convert_cpymad_element_to_fff(element):
    name = element.name.replace('.', '_').lower()
    kw_dict = dict(element.items())
    kw_dict['pos'] = kw_dict.pop('at')
    kw_dict['length'] = kw_dict.pop('l')
    kw_dict['parent'] = element.parent.name
    base_type = element.base_type.name
    return CPYMAD_TO_FFF_MAP[base_type](name, **kw_dict)


def convert_fff_element_to_cpymad(element, madx):
    element_type = element.__class__.__name__.lower()
    kwargs = copy.copy(vars(element))
    kwargs['l'] = kwargs.pop('length')
    kwargs['at'] = kwargs.pop('_position')
    kwargs.pop('name')
    kwargs.pop('parent')
    
    kw = copy.copy(kwargs)
    for key in kw.keys():
        if key not in madx.elements[element_type].keys():
            kwargs.pop(key)
    madx.command[element_type].clone(element.name, **kwargs)
    return 


def create_pyat_from_file(file_path):
    ring = at.load.matfile.load_mat(file_path, key='ring')
    ring = at.Lattice(ring)
    return ring


def export_pyat_from_lattice(lattice):
    elements = lattice._sequence_with_drifts
    seq = []
    for element in elements:
        if element.__class__.__name__ == 'Marker':
            marker = at.lattice.elements.Marker(element.name)
            seq.append(marker)
        elif element.__class__.__name__ == 'Drift':
            drift = at.lattice.elements.Drift(element.name, element.length, NumIntSteps=getattr(element, 'NumIntSteps', 20))
            seq.append(drift)
        elif element.__class__.__name__ == 'Sbend':
            dipole = at.lattice.elements.Dipole(element.name, element.length, element.angle,
                                                EntranceAngle=element.e1, ExitAngle=element.e2,
                                                PassMethod=getattr(element, 'PassMethod', 'BndMPoleSymplectic4Pass'), 
                                                NumIntSteps=getattr(element, 'NumIntSteps', 20))
            seq.append(dipole)
        elif element.__class__.__name__ == 'Rbend':
            element_temp = element.convert_to_sbend()
            dipole = at.lattice.elements.Dipole(element_temp.name, element_temp.length, element_temp.angle, 
                                                EntranceAngle=element_temp.e1, ExitAngle=element_temp.e2,
                                                PassMethod=getattr(element, 'PassMethod', 'BndMPoleSymplectic4Pass'), 
                                                NumIntSteps=getattr(element, 'NumIntSteps', 20))
            seq.append(dipole)
        elif element.__class__.__name__ == 'Quadrupole':
            quadrupole = at.lattice.elements.Quadrupole(element.name, element.length, element.k1, 
                                                PassMethod=getattr(element, 'PassMethod', 'StrMPoleSymplectic4Pass'), 
                                                NumIntSteps=getattr(element, 'NumIntSteps', 20))
            seq.append(quadrupole)
        elif element.__class__.__name__ == 'Sextupole':
            sextupole = at.lattice.elements.Sextupole(element.name, element.length, element.k2,
                                                PassMethod=getattr(element, 'PassMethod', 'StrMPoleSymplectic4Pass'), 
                                                NumIntSteps=getattr(element, 'NumIntSteps', 20))
            seq.append(sextupole)
        elif element.__class__.__name__ == 'RFCavity':
            harmonic_number = int(element.freq/(scipy.constants.c/elements[-1].pos))
            rfcavity = at.lattice.elements.RFCavity(element.name.replace('.', '_').upper(), 
                                                    element.length, voltage=element.volt, 
                                                    frequency=element.freq, 
                                                    harmonic_number=harmonic_number, 
                                                    energy=lattice.energy)
            seq.append(rfcavity)
    pyat_lattice = at.Lattice(seq, name=lattice.name, key='line', energy=lattice.energy*1e9)
    return pyat_lattice




def import_lattice_from_pyat(pyat_lattice):
    total_length = pyat_lattice.get_s_pos([-1])
    seq = []
    for element in pyat_lattice:
        if element.__class__.__name__ == 'Marker':
            marker = elements.Marker(element.FamName)
            seq.append(marker)
        if element.__class__.__name__ == 'Drift':
            drift = elements.Drift(element.FamName, length=element.Length, 
                                   PassMethod=element.PassMethod, NumIntSteps=element.NumIntSteps)
            seq.append(drift)
        elif element.__class__.__name__ == 'Dipole':
            dipole = elements.Sbend(element.FamName, length=element.Length, 
                                    PassMethod=element.PassMethod, NumIntSteps=element.NumIntSteps, 
                                    angle=element.BendingAngle, e1=element.EntranceAngle, 
                                    e2=element.ExitAngle)
            seq.append(dipole)
        elif element.__class__.__name__ == 'Quadrupole':
            quadrupole = elements.Quadrupole(element.FamName, length=element.Length, 
                                             PassMethod=element.PassMethod, NumIntSteps=element.NumIntSteps, 
                                             k1=element.PolynomB[1], k1s=element.PolynomA[1])
            seq.append(quadrupole)
        elif element.__class__.__name__ == 'Sextupole':
            sextupole = elements.Sextupole(element.FamName, length=element.Length, 
                                           PassMethod=element.PassMethod, NumIntSteps=element.NumIntSteps, 
                                           k2=element.PolynomB[2], k2s=element.PolynomA[2])
            seq.append(sextupole)
        elif element.__class__.__name__ == 'RFCavity':
            rfcavity = elements.RFCavity(element.FamName.replace('.', '_').upper(), length=element.Length, 
                                         volt=element.Voltage, freq=element.Frequency, PassMethod=element.PassMethod, 
                                         energy=element.Energy)
            seq.append(rfcavity)
    sequence = lattice.Lattice(pyat_lattice.name, seq, key='line', energy=pyat_lattice.energy) 
    return sequence
