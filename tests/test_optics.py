import lattice.conversion_functions as cf
from toolkit.pyat_functions import get_optics_pyat
import pytest
import numpy as np

@pytest.fixture(scope="module")
def example_cpymad_pyat_optics():
    madx_lattice = cf.create_cpymad_from_file('../sequences/lattice.seq', 120)
    fff_lattice = cf.import_fff_from_cpymad(madx_lattice)
    fff_lattice.convert_rbend_to_sbend()
    twm = fff_lattice.optics(engine='madx')
    twm.index = np.roll(twm.index, -1)
    twm.keyword = np.roll(twm.keyword, -1)
    twp = fff_lattice.optics(engine='pyat')
    
    twm = twm.drop(twm[twm['keyword']=='drift'].index)
    twp = twp.drop(twp[twp['keyword']=='drift'].index)
    twm.drop([fff_lattice.name+"$start", fff_lattice.name+"$end"], inplace=True)
    twp.drop([fff_lattice.name+"$start", fff_lattice.name+"$end"], inplace=True)
    return twm, twp

def test_cpymad_fff_cpymad_s(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(abs(twm.s - twp.s)) < 1e-9

def test_cpymad_fff_cpymad_orbit_x(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert sum(abs(twm.x - twp.x)) == 0

def test_cpymad_fff_cpymad_orbit_y(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert sum(abs(twm.y - twp.y)) == 0

def test_cpymad_fff_cpymad_orbit_px(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert sum(abs(twm.px - twp.px)) == 0

def test_cpymad_fff_cpymad_orbit_py(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert sum(abs(twm.py - twp.py)) == 0

def test_cpymad_fff_cpymad_betax(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs((twm.betx - twp.betx)/twm.betx)) < 1e-4

def test_cpymad_fff_cpymad_betay(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs((twm.bety - twp.bety)/twm.bety)) < 1e-4

def test_cpymad_fff_cpymad_disp_x(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs(twm.dx - twp.dx)) < 1e-4 

def test_cpymad_fff_cpymad_disp_y(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs(twm.dy - twp.dy)) < 1e-4 

def test_cpymad_fff_cpymad_alfa_x(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs(twm.alfx - twp.alfx)) < 1e-4 

def test_cpymad_fff_cpymad_alfa_y(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs(twm.alfy - twp.alfy)) < 1e-4 

def test_cpymad_fff_cpymad_phase_x(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs((twm.mux - twp.mux)/twm.mux)) < 1e-4 

def test_cpymad_fff_cpymad_phase_y(example_cpymad_pyat_optics):
    twm, twp = example_cpymad_pyat_optics
    assert max(np.abs(twm.muy - twp.muy)) < 1e-4 
