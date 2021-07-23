import conversion_functions as cf
import pytest
from pyat_functions import get_optics_pyat


@pytest.fixture(scope="module")
def example_cpymad_fff_cpymad():
    madx_lattice = cf.create_cpymad_from_file('lattice.seq', 120)
    fff_lattice = cf.import_lattice_from_cpymad(madx_lattice)
    madx_lattice_new = cf.export_cpymad_from_lattice(fff_lattice)
    madx_lattice.use('l000013')
    madx_lattice_new.use('l000013')
    twiss = madx_lattice.twiss(sequence='l000013')
    twiss_new = madx_lattice_new.twiss(sequence='l000013')
    return twiss, twiss_new


def test_cpymad_fff_cpymad_s(example_cpymad_fff_cpymad):
    twiss, twiss_new = example_cpymad_fff_cpymad
    assert sum(abs(twiss.s - twiss_new.s)) == 0


def test_cpymad_fff_cpymad_orbit(example_cpymad_fff_cpymad):
    twiss, twiss_new = example_cpymad_fff_cpymad
    assert sum(abs(twiss.x - twiss_new.x)) == 0 and\
           sum(abs(twiss.y - twiss_new.y)) == 0


def test_cpymad_fff_cpymad_beta(example_cpymad_fff_cpymad):
    twiss, twiss_new = example_cpymad_fff_cpymad
    assert sum(abs(twiss.betx - twiss_new.betx)) == 0 and\
           sum(abs(twiss.bety - twiss_new.bety)) == 0


def test_cpymad_fff_cpymad_disp(example_cpymad_fff_cpymad):
    twiss, twiss_new = example_cpymad_fff_cpymad
    assert sum(abs(twiss.dx - twiss_new.dx)) == 0 and\
           sum(abs(twiss.dy - twiss_new.dy)) == 0


def test_cpymad_fff_cpymad_alfa(example_cpymad_fff_cpymad):
    twiss, twiss_new = example_cpymad_fff_cpymad
    assert sum(abs(twiss.alfx - twiss_new.alfx)) == 0 and\
           sum(abs(twiss.alfy - twiss_new.alfy)) == 0


def test_cpymad_fff_cpymad_phase(example_cpymad_fff_cpymad):
    twiss, twiss_new = example_cpymad_fff_cpymad
    assert sum(abs(twiss.mux - twiss_new.mux)) == 0 and\
           sum(abs(twiss.muy - twiss_new.muy)) == 0



@pytest.fixture(scope="module")
def example_pyat_fff_pyat():
    pyat_lattice = cf.create_pyat_from_file('fcch_norad.mat')
    fff_lattice = cf.import_lattice_from_pyat(pyat_lattice)
    pyat_lattice_new = cf.export_pyat_from_lattice(fff_lattice)
    lin, s = get_optics_pyat(pyat_lattice, radiation=False)
    lin_new, s_new = get_optics_pyat(pyat_lattice_new, radiation=False)
    return lin, lin_new, s, s_new


def test_pyat_fff_pyat_s(example_pyat_fff_pyat):
    lin, lin_new, s, s_new = example_pyat_fff_pyat
    assert sum(abs(s - s_new)) == 0


def test_pyat_fff_pyat_orbit(example_pyat_fff_pyat):
    lin, lin_new, _, _ = example_pyat_fff_pyat
    assert sum(abs(lin.closed_orbit[:,0] - lin_new.closed_orbit[:,0])) == 0 and\
           sum(abs(lin.closed_orbit[:,1] - lin_new.closed_orbit[:,1])) == 0 and\
           sum(abs(lin.closed_orbit[:,2] - lin_new.closed_orbit[:,2])) == 0 and\
           sum(abs(lin.closed_orbit[:,3] - lin_new.closed_orbit[:,3])) == 0 and\
           sum(abs(lin.closed_orbit[:,4] - lin_new.closed_orbit[:,4])) == 0 and\
           sum(abs(lin.closed_orbit[:,5] - lin_new.closed_orbit[:,5])) == 0


def test_pyat_fff_pyat_beta(example_pyat_fff_pyat):
    lin, lin_new, _, _ = example_pyat_fff_pyat
    assert sum(abs(lin.beta[:,0] - lin_new.beta[:,0])) == 0 and\
           sum(abs(lin.beta[:,1] - lin_new.beta[:,1])) == 0


def test_pyat_fff_pyat_disp(example_pyat_fff_pyat):
    lin, lin_new, _, _ = example_pyat_fff_pyat
    assert sum(abs(lin.dispersion[:,0] - lin_new.dispersion[:,0])) == 0 and\
           sum(abs(lin.dispersion[:,1] - lin_new.dispersion[:,1])) == 0


def test_pyat_fff_pyat_alfa(example_pyat_fff_pyat):
    lin, lin_new, _, _ = example_pyat_fff_pyat
    assert sum(abs(lin.alpha[:,0] - lin_new.alpha[:,0])) == 0 and\
           sum(abs(lin.alpha[:,1] - lin_new.alpha[:,1])) == 0


def test_pyat_fff_pyat_phase(example_pyat_fff_pyat):
    lin, lin_new, _, _ = example_pyat_fff_pyat
    assert sum(abs(lin.mu[:,0] - lin_new.mu[:,0])) == 0 and\
           sum(abs(lin.mu[:,1] - lin_new.mu[:,1])) == 0



# @pytest.fixture(scope="module")
# def example_cpymad_fff_pyat_fff_cpymad():
#     madx_lattice = cf.create_cpymad_from_file('lattice.seq', 120)
#     fff_lattice = cf.import_lattice_from_cpymad(madx_lattice)
#     pyat_lattice = cf.export_pyat_from_lattice(fff_lattice)
#     fff_lattice_new = cf.import_lattice_from_pyat(pyat_lattice)
#     madx_lattice_new = cf.export_cpymad_from_lattice(fff_lattice_new)
#     madx_lattice.use('l000013')
#     madx_lattice_new.use('l000013')
#     twiss = madx_lattice.twiss(sequence='l000013')
#     twiss_new = madx_lattice_new.twiss(sequence='l000013')
#     return twiss, twiss_new
# 
# 
# def test_cpymad_fff_pyat_fff_cpymad_s(example_cpymad_fff_pyat_fff_cpymad):
#     twiss, twiss_new = example_cpymad_fff_pyat_fff_cpymad
#     assert sum(abs(twiss.s - twiss_new.s)) == 0
# 
# 
# def test_cpymad_fff_pyat_fff_cpymad_orbit(example_cpymad_fff_pyat_fff_cpymad):
#     twiss, twiss_new = example_cpymad_fff_pyat_fff_cpymad
#     assert sum(abs(twiss.x - twiss_new.x)) == 0 and\
#            sum(abs(twiss.y - twiss_new.y)) == 0
# 
# 
# def test_cpymad_fff_pyat_fff_cpymad_beta(example_cpymad_fff_pyat_fff_cpymad):
#     twiss, twiss_new = example_cpymad_fff_pyat_fff_cpymad
#     assert sum(abs(twiss.betx - twiss_new.betx)) == 0 and\
#            sum(abs(twiss.bety - twiss_new.bety)) == 0
# 
# 
# def test_cpymad_fff_pyat_fff_cpymad_disp(example_cpymad_fff_pyat_fff_cpymad):
#     twiss, twiss_new = example_cpymad_fff_pyat_fff_cpymad
#     assert sum(abs(twiss.dx - twiss_new.dx)) == 0 and\
#            sum(abs(twiss.dy - twiss_new.dy)) == 0
# 
# 
# def test_cpymad_fff_pyat_fff_cpymad_alfa(example_cpymad_fff_pyat_fff_cpymad):
#     twiss, twiss_new = example_cpymad_fff_pyat_fff_cpymad
#     assert sum(abs(twiss.alfx - twiss_new.alfx)) == 0 and\
#            sum(abs(twiss.alfy - twiss_new.alfy)) == 0
# 
# 
# def test_cpymad_fff_pyat_fff_cpymad_phase(example_cpymad_fff_pyat_fff_cpymad):
#     twiss, twiss_new = example_cpymad_fff_pyat_fff_cpymad
#     assert sum(abs(twiss.mux - twiss_new.mux)) == 0 and\
#            sum(abs(twiss.muy - twiss_new.muy)) == 0
# 
# 
# 
# 
# 
# 
# @pytest.fixture(scope="module")
# def example_pyat_fff_cpymad_fff_pyat():
#     pyat_lattice = cf.create_pyat_from_file('fcch_norad.mat')
#     fff_lattice = cf.import_lattice_from_pyat(pyat_lattice)
#     madx_lattice = cf.export_cpymad_from_lattice(fff_lattice)
#     fff_lattice_new = cf.import_lattice_from_cpymad(madx_lattice)
#     pyat_lattice_new = cf.export_pyat_from_lattice(fff_lattice_new)
#     lin, s = get_optics_pyat(pyat_lattice, radiation=False)
#     lin_new, s_new = get_optics_pyat(pyat_lattice_new, radiation=False)
#     return lin, lin_new, s, s_new
# 
# def test_pyat_fff_cpymad_fff_pyat_s(example_pyat_fff_cpymad_fff_pyat):
#     lin, lin_new, s, s_new = example_pyat_fff_cpymad_fff_pyat
#     assert sum(abs(s - s_new)) == 0
# 
# 
# def test_pyat_fff_cpymad_fff_pyat_orbit(example_pyat_fff_cpymad_fff_pyat):
#     lin, lin_new, _, _ = example_pyat_fff_cpymad_fff_pyat
#     assert sum(abs(lin.closed_orbit[:,0] - lin_new.closed_orbit[:,0])) == 0 and\
#            sum(abs(lin.closed_orbit[:,1] - lin_new.closed_orbit[:,1])) == 0 and\
#            sum(abs(lin.closed_orbit[:,2] - lin_new.closed_orbit[:,2])) == 0 and\
#            sum(abs(lin.closed_orbit[:,3] - lin_new.closed_orbit[:,3])) == 0 and\
#            sum(abs(lin.closed_orbit[:,4] - lin_new.closed_orbit[:,4])) == 0 and\
#            sum(abs(lin.closed_orbit[:,5] - lin_new.closed_orbit[:,5])) == 0
# 
# 
# def test_pyat_fff_cpymad_fff_pyat_beta(example_pyat_fff_cpymad_fff_pyat):
#     lin, lin_new, _, _ = example_pyat_fff_cpymad_fff_pyat
#     assert sum(abs(lin.beta[:,0] - lin_new.beta[:,0])) == 0 and\
#            sum(abs(lin.beta[:,1] - lin_new.beta[:,1])) == 0
# 
# 
# def test_pyat_fff_cpymad_fff_pyat_disp(example_pyat_fff_cpymad_fff_pyat):
#     lin, lin_new, _, _ = example_pyat_fff_cpymad_fff_pyat
#     assert sum(abs(lin.dispersion[:,0] - lin_new.dispersion[:,0])) == 0 and\
#            sum(abs(lin.dispersion[:,1] - lin_new.dispersion[:,1])) == 0
# 
# 
# def test_pyat_fff_cpymad_fff_pyat_alfa(example_pyat_fff_cpymad_fff_pyat):
#     lin, lin_new, _, _ = example_pyat_fff_cpymad_fff_pyat
#     assert sum(abs(lin.alpha[:,0] - lin_new.alpha[:,0])) == 0 and\
#            sum(abs(lin.alpha[:,1] - lin_new.alpha[:,1])) == 0
# 
# 
# def test_pyat_fff_cpymad_fff_pyat_phase(example_pyat_fff_cpymad_fff_pyat):
#     lin, lin_new, _, _ = example_pyat_fff_cpymad_fff_pyat
#     assert sum(abs(lin.mu[:,0] - lin_new.mu[:,0])) == 0 and\
#            sum(abs(lin.mu[:,1] - lin_new.mu[:,1])) == 0
# 
