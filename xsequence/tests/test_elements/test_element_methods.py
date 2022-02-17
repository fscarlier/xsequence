"""
Module tests.test_elements.test_element_methods
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a test module to test element methods.
"""

from xsequence.elements import *
from pytest import mark


@mark.parametrize('el1, el2',
                 [(BaseElement(),                                        BaseElement()   ),
                  (BaseElement(length=1.0),                              BaseElement(length=1.0)   ),
                  (BaseElement(length=0.0),                              BaseElement(length=0.0)   ),
                  (Quadrupole(length=1.0, k1=0.4, k1s=1.2),              Quadrupole(length=1.0, k1=0.4, k1s=1.2)   ),
                  (Quadrupole(length=3.0, k1=0.4, k1s=1.2),              Quadrupole(length=3.0, k1=0.4, k1s=1.2)   ),
                  (SectorBend(length=2.0, angle=0.3),                    SectorBend(length=2.0, angle=0.3)   ),
                  (SectorBend(length=2.0, angle=0.3, e1=0.01, e2=0.011), SectorBend(length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                 ])
def test_eq_method(el1, el2):
    assert el1 == el2


@mark.parametrize('el1, el2',
                 [(BaseElement(),                                        Quadrupole()   ),
                  (BaseElement(),                                        BaseElement()   ),
                  (BaseElement(length=1.0),                              BaseElement(length=1.1)   ),
                  (BaseElement(length=0.0),                              BaseElement(length=0.1)   ),
                  (Quadrupole(length=1.0, k1=0.4, k1s=1.2),              Quadrupole(length=1.0, k1=0.1, k1s=1.2)   ),
                  (Quadrupole(length=3.0, k1=0.4, k1s=1.2),              Quadrupole(length=3.0, k1=0.4, k1s=1.1)   ),
                  (Quadrupole(length=2.0, k1=0.2999),                    Quadrupole(length=2.0, k1=0.3)   ),
                  (SectorBend(length=2.0, angle=0.3),                    SectorBend(length=2.0, angle=0.2)   ),
                  (SectorBend(length=1.0, angle=0.3),                    SectorBend(length=2.0, angle=0.3)   ),
                  (SectorBend(length=2.0, angle=0.3, e1=0.01, e2=0.012), SectorBend(length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                  (SectorBend(length=2.0, angle=0.3, e1=0.02, e2=0.011), SectorBend(length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                 ])
def test_neq_method(el1, el2):
    assert el1 != el2



