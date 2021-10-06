"""
Module tests.test_elements.test_element_cpymad
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a test module to test correct element imports from cpymad.
"""

import pytest
import fsf.elements as el
from pytest import mark
from cpymad.madx import Madx

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
    quad = el.Quadrupole.from_cpymad(md.elements[name])
    assert quad.length == md.elements[name].l


@mark.parametrize('name, l, k1',
                 [('q1', 1, 1.2),
                  ('q2', 1, -0.2),
                  ('q3', 1, 123.5092348928)])
def test_cpymad_quadrupole_import_k1(name, l, k1):
    md = Madx()
    md.command['quadrupole'].clone(name, l=l)
    md.elements[name].k1 = k1 
    quad = el.Quadrupole.from_cpymad(md.elements[name])
    assert quad.k1 == md.elements[name].k1


@mark.parametrize('name, l, k1s',
                 [('q1', 1, 1.2),
                  ('q2', 1, -0.2),
                  ('q3', 1, 123.5092348928)])
def test_cpymad_quadrupole_import_k1s(name, l, k1s):
    md = Madx()
    md.command['quadrupole'].clone(name, l=l)
    md.elements[name].k1s = k1s
    quad = el.Quadrupole.from_cpymad(md.elements[name])
    assert quad.k1s == md.elements[name].k1s


