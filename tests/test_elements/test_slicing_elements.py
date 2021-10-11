"""
Module tests.test_elements.test_slicing_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a test module to test correct slicing of elements.
"""

from fsf.lattice import Lattice
from fsf.elements import *
from pytest import mark
import math


@mark.parametrize('name, nslices, length, delta, distance',
                 [('el1_2', 2,  1.0, 1/6, 2/3),
                  ('el1_3', 3,  1.0, 1/8, 3/8),
                  ('el1_4', 4,  1.0, 1/10, 4/15),
                  ('el1_5', 5,  1.0, 1/12, 5/24),
                  ('el2_2', 2,  3.4, 3.4*1/6, 3.4*2/3),
                  ('el2_3', 3,  3.4, 3.4*1/8, 3.4*3/8),
                  ('el2_4', 4,  3.4, 3.4*1/10, 3.4*4/15),
                  ('el2_5', 5,  3.4, 3.4*1/12, 3.4*5/24)])
def test_teapot_slice_distances(name, nslices, length, delta, distance):
    el = Element(name, length=length)
    dl, dis = el.teapot_slicing(nslices)
    errors = []
    if not math.isclose(delta, dl, abs_tol=1e-15):
        errors.append(f"Error: TEAPOT delta not correct, should be {delta}")
    if not math.isclose(distance, dis, abs_tol=1e-15):
        errors.append(f"Error: TEAPOT distance not correct, should be {distance}")
    assert not errors, "errors occured:\n{}".format("\n".join(errors))


def test_teapot_slice_Sbend_4_slices():
    sb1 = Sbend('sb1', length=15.0, position=7.5, angle=0.30)
    sliced_element = sb1.slice_element(num_slices=4)
    
    ref = [DipEdge('sb1_edge_entrance', position=0.0, h=0.02, side='entrance'), 
           ThinMultipole('sb1_0', position=1.5, knl=[0.075]), 
           ThinMultipole('sb1_1', position=5.5, knl=[0.075]), 
           ThinMultipole('sb1_2', position=9.5, knl=[0.075]), 
           ThinMultipole('sb1_3', position=13.5, knl=[0.075]), 
           DipEdge('sb1_edge_exit', position=15.0, h=0.02, side='exit')]

    for idx, el in enumerate(ref):
        assert el == sliced_element[idx]       


def test_teapot_slice_Sbend_3_slices():
    sb1 = Sbend('sb1', length=15.0, position=7.5, angle=0.30)
    sliced_element = sb1.slice_element(num_slices=3)
    
    ref = [DipEdge('sb1_edge_entrance', position=0.0, h=0.02, side='entrance'), 
           ThinMultipole('sb1_0', position=1.875, knl=[0.1]), 
           ThinMultipole('sb1_1', position=7.5, knl=[0.1]), 
           ThinMultipole('sb1_2', position=13.125, knl=[0.1]), 
           DipEdge('sb1_edge_exit', position=15.0, h=0.02, side='exit')]

    for idx, el in enumerate(ref):
        print(el)
        print(sliced_element[idx])
        assert el == sliced_element[idx]     



# def test_teapot_slice_Sbend_4_slices():
#     sb1 = Sbend('sb1', length=2.0, position=1.0, angle=0.4)
#     sliced_element = sb1.slice_element(num_slices=4)
#     
#     ref = [DipEdge('sb1_edge_entrance', position=0.0, h=0.2, side='entrance'), 
#            ThinMultipole('sb1_0', position=0.2, knl=[0.1]), 
#            ThinMultipole('sb1_1', position=0.7333333333333333, knl=[0.1]), 
#            ThinMultipole('sb1_2', position=1.2666666666666666, knl=[0.1]), 
#            ThinMultipole('sb1_3', position=1.8, knl=[0.1]), 
#            DipEdge('sb1_edge_exit', position=2.0, h=0.2, side='exit')] 
#     for idx, el in enumerate(ref):
#         assert el == sliced_element[idx]     

'''
lat_sl = lat.slice_lattice()
thin_lattice = Lattice('lat', lat_sl, key='sequence')


# Sbends and Rbends in sequence representation
sb1 = Sbend('sb1', length=1.0, angle=0.2, position=1)
sb2 = Sbend('sb2', length=1.0, angle=0.4, position=3)
rb1 = sb1.convert_to_rbend()
rb2 = sb2.convert_to_rbend()

ms = Marker('start', position=0)
me = Marker('end', position=5)

lat = Lattice('lat', [ms, sb1, sb2, me], key='sequence')
for q in lat.get_class('Sbend'):
    q.int_steps = 3

lat_sl = lat.slice_lattice()
thin_lattice = Lattice('lat', lat_sl, key='sequence')


# Quadrupoles and Drifts in line representation
q1 = Quadrupole('q1', length=1.0, k1=4.0)
q2 = Quadrupole('q2', length=1.0, k1=4.0)
q3 = Quadrupole('q3', length=1.0, k1=4.0)
q4 = Quadrupole('q4', length=1.0, k1=4.0)
q5 = Quadrupole('q5', length=1.0, k1=4.0)

d1 = Drift('d1', length=2.0)
d2 = Drift('d2', length=2.0)
d3 = Drift('d3', length=2.0)
d4 = Drift('d4', length=2.0)
d5 = Drift('d5', length=2.0)

ms = Marker('start')
me = Marker('end')

lat = Lattice('lat', [ms, q1, d1, q2, d2, q3, d3, q4, d4, q5, d5, me], key='line')
for q in lat.get_class('Quadrupole'):
    q.int_steps = 3

lat_sl = lat.slice_lattice()
thin_lattice = Lattice('lat', lat_sl, key='sequence')

'''
