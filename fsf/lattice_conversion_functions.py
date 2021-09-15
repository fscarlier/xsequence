from cpymad.madx import Madx
import at
import fsf.element_conversion_functions as ecf


def create_cpymad_from_file(sequence_path, energy, particle_type='electron', logging=True):
    if logging:
        madx = Madx(command_log='log.madx')
    else:
        madx = Madx()

    madx.option(echo=False, info=False, debug=False)
    madx.call(file=sequence_path)
    madx.input('SET, FORMAT="25.20e";')
    madx.command.beam(particle=particle_type, energy=energy)
    return madx


def create_pyat_from_file(file_path):
    ring = at.load.matfile.load_mat(file_path, key='ring')
    ring = at.Lattice(ring)
    return ring


def create_global_elements_from_cpymad(madx):
    idx = 0
    global_elements = []
    while '$start' not in madx.elements[idx].name:
        if madx.elements[idx].name not in madx.base_types:
            gl_ele = ecf.convert_cpymad_element_to_fsf(madx.elements[idx])
            global_elements.append(gl_ele)
        idx += 1
    return global_elements


def export_to_cpymad(fsf_lattice):
    # TODO: - Should develop complete constraint on allowed keyword arguments for cpymad
    #       - Reproduce inheritance from global elements
    madx = Madx(command_log='log.madx')
    madx.option(echo=False, info=False, debug=False)
    seq_command = ''
    global_elements_defined = False
    
    try: 
        global_elements = fsf_lattice.global_elements
        for element in global_elements:
            element.to_cpymad(madx)
        global_elements_defined = True
    except AttributeError:
        print("No global elements in cpymad instance")

    elements = fsf_lattice.sequence
    for element in elements[1:-1]:
        if not global_elements_defined:
            element.to_cpymad(madx)
            seq_command += f'{element.name}, at={element.pos}  ;\n'
        else:
            seq_command += f'{element.name}: {element.parent}, at={element.pos}  ;\n'
    
    madx.input(f'{fsf_lattice.name}: sequence, refer=centre, l={fsf_lattice.sequence[-1].pos};')
    madx.input(seq_command)
    madx.input('endsequence;')
    madx.command.beam(particle='electron', energy=fsf_lattice.energy)
    return madx


def export_to_pyat(fsf_lattice):
    elements = fsf_lattice.line
    seq = []
    for element in elements:
        pyat_el = element.to_pyat() 
        seq.append(pyat_el)
    pyat_lattice = at.Lattice(seq, name=fsf_lattice.name, key='line', energy=fsf_lattice.energy*1e9)
    return pyat_lattice
