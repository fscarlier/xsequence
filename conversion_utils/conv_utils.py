from cpymad.madx import Madx
import at


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


