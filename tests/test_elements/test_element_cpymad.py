"""
Module tests.test_elements.test_element_cpymad
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a test module to test correct element imports from cpymad.
"""

import pytest
import fsf.elements
from pytest import mark
from cpymad.madx import Madx
from conversion_utils import conv_utils
from pathlib import Path
TEST_SEQ_DIR = Path(__file__).parent.parent / "test_sequences"


"""
Quadrupole tests
"""

@mark.parametrize('name, l',
                 [('q1', 1.2),
                  ('q2', 0.2),
                  ('q3', 123.5092348928)])
def test_cpymad_quadrupole_import_l(name, l):
    md = Madx()
    md.command['quadrupole'].clone(name)
    md.elements[name].l = l
    quad = fsf.elements.Quadrupole.from_cpymad(md.elements[name])
    assert quad.length == md.elements[name].l


@mark.parametrize('name, l, k1',
                 [('q1', 1, 1.2),
                  ('q2', 1, -0.2),
                  ('q3', 1, 123.5092348928)])
def test_cpymad_quadrupole_import_k1(name, l, k1):
    md = Madx()
    md.command['quadrupole'].clone(name, l=l)
    md.elements[name].k1 = k1 
    quad = fsf.elements.Quadrupole.from_cpymad(md.elements[name])
    assert quad.k1 == md.elements[name].k1


@mark.parametrize('name, l, k1s',
                 [('q1', 1, 1.2),
                  ('q2', 1, -0.2),
                  ('q3', 1, 123.5092348928)])
def test_cpymad_quadrupole_import_k1s(name, l, k1s):
    md = Madx()
    md.command['quadrupole'].clone(name, l=l)
    md.elements[name].k1s = k1s
    quad = fsf.elements.Quadrupole.from_cpymad(md.elements[name])
    assert quad.k1s == md.elements[name].k1s

"""
Element by element tests cpymad back to cpymad (FCC-ee lattice)
"""

@pytest.fixture(scope="module")
def example_madx_lattice():
    madx_lattice = Madx()
    madx_lattice.call(str(TEST_SEQ_DIR / "lhc.seq"))
    madx_lattice.call(str(TEST_SEQ_DIR / "optics.madx"))
    # madx_lattice = conv_utils.create_cpymad_from_file(str(TEST_SEQ_DIR / "lattice.seq"), 120)
    return madx_lattice    


def test_quadrupoles(example_madx_lattice):
    madx_lattice = example_madx_lattice
    md = Madx()
    results = []
    for idx in range(44,len(madx_lattice.elements)):
        el = madx_lattice.elements[idx]
        if el.base_type.name == 'quadrupole':
            fsf.elements.Quadrupole.from_cpymad(el).to_cpymad(md)
            if el == md.elements[el.name]:
                results.append(True)
    assert all(results)


def test_sextupoles(example_madx_lattice):
    madx_lattice = example_madx_lattice
    md = Madx()
    results = []
    for idx in range(44,len(madx_lattice.elements)):
        el = madx_lattice.elements[idx]
        if el.base_type.name == 'sextupole':
            fsf.elements.Sextupole.from_cpymad(el).to_cpymad(md)
            if el == md.elements[el.name]:
                results.append(True)
    assert all(results)


def test_marker(example_madx_lattice):
    madx_lattice = example_madx_lattice
    md = Madx()
    results = []
    for idx in range(44,len(madx_lattice.elements)):
        el = madx_lattice.elements[idx]
        if el.base_type.name == 'marker':
            fsf.elements.Marker.from_cpymad(el).to_cpymad(md)
            if el == md.elements[el.name]:
                results.append(True)
    assert all(results)


def test_rbend(example_madx_lattice):
    madx_lattice = example_madx_lattice
    md = Madx()
    results = []
    for idx in range(44,len(madx_lattice.elements)):
        el = madx_lattice.elements[idx]
        if el.base_type.name == 'rbend':
            fsf.elements.Rbend.from_cpymad(el).to_cpymad(md)
            if el == md.elements[el.name]:
                results.append(True)
    assert all(results)

