import xsequence.lattice as lat
from xsequence.helpers.pyat_functions import get_optics_pyat
import pytest
from xsequence.conversion_utils import conv_utils


@pytest.fixture(scope="module")
def example_cpymad_xsequence_pyat():
    """
    Create cpymad instance from import and export through xsequence
    
    Returns:
        Old and new twiss tables from cpymad
    """
    madx_lattice = conv_utils.create_cpymad_from_file('./test_sequences/lattice.seq', 120)
    xsequence_lattice = lat.Lattice.from_cpymad(madx_lattice, 'l000013')
    pyat_lattice = xsequence_lattice.to_pyat()
    lin, s = get_optics_pyat(pyat_lattice, radiation=False)
    madx_lattice.use('l000013')
    twiss = madx_lattice.twiss(sequence='l000013')
    return twiss, lin, s 

def test_cpymad_xsequence_cpymad_s(example_cpymad_xsequence_cpymad):
    twiss, twiss_new = example_cpymad_xsequence_cpymad
    assert sum(abs(twiss.s - twiss_new.s)) == 0

def test_cpymad_xsequence_cpymad_orbit(example_cpymad_xsequence_cpymad):
    twiss, twiss_new = example_cpymad_xsequence_cpymad
    assert sum(abs(twiss.x - twiss_new.x)) == 0 and\
           sum(abs(twiss.y - twiss_new.y)) == 0

def test_cpymad_xsequence_cpymad_beta(example_cpymad_xsequence_cpymad):
    twiss, twiss_new = example_cpymad_xsequence_cpymad
    assert sum(abs(twiss.betx - twiss_new.betx)) == 0 and\
           sum(abs(twiss.bety - twiss_new.bety)) == 0

def test_cpymad_xsequence_cpymad_disp(example_cpymad_xsequence_cpymad):
    twiss, twiss_new = example_cpymad_xsequence_cpymad
    assert sum(abs(twiss.dx - twiss_new.dx)) == 0 and\
           sum(abs(twiss.dy - twiss_new.dy)) == 0

def test_cpymad_xsequence_cpymad_alfa(example_cpymad_xsequence_cpymad):
    twiss, twiss_new = example_cpymad_xsequence_cpymad
    assert sum(abs(twiss.alfx - twiss_new.alfx)) == 0 and\
           sum(abs(twiss.alfy - twiss_new.alfy)) == 0

def test_cpymad_xsequence_cpymad_phase(example_cpymad_xsequence_cpymad):
    twiss, twiss_new = example_cpymad_xsequence_cpymad
    assert sum(abs(twiss.mux - twiss_new.mux)) == 0 and\
           sum(abs(twiss.muy - twiss_new.muy)) == 0


