"""
Module tests.test_lattice_conversions.test_cpymad_xsequence_cpymad
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a test module to test consistency for converting back and forth from cpymad.
"""

from xsequence.lattice import Lattice
import pytest
from cpymad.madx import Madx
from xsequence.conversion_utils import conv_utils
from pathlib import Path

TEST_SEQ_DIR = Path(__file__).parent.parent / "test_sequences"

@pytest.fixture(scope="module")
def example_cpymad_xsequence_cpymad():
    """
    Create cpymad instance from import and export through xsequence
    
    Returns:
        Old and new twiss tables from cpymad
    """
    
    
    seq_name = 'lhcb1'
    madx_lattice=Madx(stdout=False)
    madx_lattice.call(str(TEST_SEQ_DIR / "lhc.seq"))
    madx_lattice.call(str(TEST_SEQ_DIR / "optics.madx"))
    madx_lattice.options.rbarc = True
    xsequence_lattice = Lattice.from_cpymad(madx_lattice, seq_name, dependencies=True)
    madx_lattice_new = xsequence_lattice.to_cpymad()
    
    madx_lattice.command.beam(particle='proton')
    madx_lattice.use(seq_name)
    twiss = madx_lattice.twiss(sequence=seq_name)
    
    madx_lattice_new.command.beam(particle='proton')
    madx_lattice_new.use(seq_name)
    twiss_new = madx_lattice_new.twiss(sequence=seq_name)
    
    return twiss, twiss_new

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

