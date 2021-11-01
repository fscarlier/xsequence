"""
Module tests.test_elements.test_element_methods
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a test module to test element methods.
"""

from fsf.elements import *
from pytest import mark


@mark.parametrize('el1, el2',
                 [(BaseElement('el_0'),                                      BaseElement('el_0')   ),
                  (BaseElement('el_1', length=1.0),                          BaseElement('el_1', length=1.0)   ),
                  (BaseElement('el_2', length=0.0),                          BaseElement('el_2', length=0.0)   ),
                  (Quadrupole('el_3', length=1.0, k1=0.4, k1s=1.2),          Quadrupole('el_3', length=1.0, k1=0.4, k1s=1.2)   ),
                  (Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.2),          Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.2)   ),
                  (SectorBend('el_5', length=2.0, angle=0.3),                    SectorBend('el_5', length=2.0, angle=0.3)   ),
                  (SectorBend('el_6', length=2.0, angle=0.3, e1=0.01, e2=0.011), SectorBend('el_6', length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                 ])
def test_eq_method(el1, el2):
    assert el1 == el2


@mark.parametrize('el1, el2',
                 [(BaseElement('el_0'),                                           Quadrupole('el_0')   ),
                  (BaseElement('el_0'),                                           BaseElement('el_1')   ),
                  (BaseElement('el_1', length=1.0),                               BaseElement('el_1', length=1.1)   ),
                  (BaseElement('el_2', length=0.0),                               BaseElement('el_2', length=0.1)   ),
                  (Quadrupole('el_3', length=1.0, k1=0.4, k1s=1.2),               Quadrupole('el_3', length=1.0, k1=0.1, k1s=1.2)   ),
                  (Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.2),               Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.1)   ),
                  (Quadrupole('el_8', length=2.0, k1=0.2999),                     Quadrupole('el_8', length=2.0, k1=0.3)   ),
                  (SectorBend('el_9', length=2.0, angle=0.3),                     SectorBend('el_9', length=2.0, angle=0.2)   ),
                  (SectorBend('el_10', length=1.0, angle=0.3),                    SectorBend('el_10', length=2.0, angle=0.3)   ),
                  (SectorBend('el_11', length=2.0, angle=0.3, e1=0.01, e2=0.012), SectorBend('el_11', length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                  (SectorBend('el_12', length=2.0, angle=0.3, e1=0.02, e2=0.011), SectorBend('el_12', length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                 ])
def test_neq_method(el1, el2):
    assert el1 != el2



