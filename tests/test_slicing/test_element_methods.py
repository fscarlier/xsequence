from fsf.elements import *
from pytest import mark


@mark.parametrize('el1, el2',
                 [(Element('el_0'),                                          Element('el_0')   ),
                  (Element('el_1', length=1.0),                              Element('el_1', length=1.0)   ),
                  (Element('el_2', length=0.0),                              Element('el_2', length=0.0)   ),
                  (Quadrupole('el_3', length=1.0, k1=0.4, k1s=1.2),          Quadrupole('el_3', length=1.0, k1=0.4, k1s=1.2)   ),
                  (Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.2),          Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.2)   ),
                  (Quadrupole('el_6', length=1.3, knl=[0.4]),                Quadrupole('el_6', length=1.3, knl=[0.4])   ),
                  (Quadrupole('el_7', length=1.0, k1=0.3),                   Quadrupole('el_7', length=1.0, knl=[0, 0.3])   ),
                  (Quadrupole('el_8', length=2.0, knl=[0, 0.299999999999]),  Quadrupole('el_8', length=2.0, knl=[0, 0.3])   ),
                  (Sbend('el_9', length=2.0, angle=0.3),                     Sbend('el_9', length=2.0, angle=0.3)   ),
                  (Sbend('el_10', length=2.0, angle=0.3, e1=0.01, e2=0.011), Sbend('el_10', length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                 ])
def test_eq_method(el1, el2):
    assert el1 == el2


@mark.parametrize('el1, el2',
                 [(Element('el_0'),                                          Element('el_1')   ),
                  (Element('el_1', length=1.0),                              Element('el_1', length=1.1)   ),
                  (Element('el_2', length=0.0),                              Element('el_2', length=0.1)   ),
                  (Quadrupole('el_3', length=1.0, k1=0.4, k1s=1.2),          Quadrupole('el_3', length=1.0, k1=0.1, k1s=1.2)   ),
                  (Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.2),          Quadrupole('el_4', length=3.0, k1=0.4, k1s=1.1)   ),
                  (Quadrupole('el_5', length=1.0, knl=[0, 0.4]),             Quadrupole('el_5', length=1.0, knl=[0, 0.7])   ),
                  (Quadrupole('el_7', length=1.0, k1=0.3),                   Quadrupole('el_7', length=1.0, knl=[0, 0.3])   ),
                  (Quadrupole('el_8', length=2.0, knl=[0, 0.2999]),          Quadrupole('el_8', length=2.0, knl=[0, 0.3])   ),
                  (Sbend('el_9', length=2.0, angle=0.3),                     Sbend('el_9', length=2.0, angle=0.2)   ),
                  (Sbend('el_10', length=1.0, angle=0.3),                    Sbend('el_10', length=2.0, angle=0.3)   ),
                  (Sbend('el_11', length=2.0, angle=0.3, e1=0.01, e2=0.012), Sbend('el_11', length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                  (Sbend('el_12', length=2.0, angle=0.3, e1=0.02, e2=0.011), Sbend('el_12', length=2.0, angle=0.3, e1=0.01, e2=0.011)   ),
                 ])
def test_eq_method(el1, el2):
    assert el1 != el2



