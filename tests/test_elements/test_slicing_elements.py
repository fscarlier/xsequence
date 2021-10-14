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


def test_teapot_slice_Sbend_4_slices():
    sb1 = Sbend('sb1', length=15.0, position=7.5, angle=0.30)
    sliced_element = sb1.slice_element(num_slices=4)
    
    ref = [DipoleEdge('sb1_edge_entrance', position=0.0, h=0.02, side='entrance'), 
           ThinMultipole('sb1_0', position=1.5, knl=[0.075], rad_length=15/4), 
           ThinMultipole('sb1_1', position=5.5, knl=[0.075], rad_length=15/4), 
           ThinMultipole('sb1_2', position=9.5, knl=[0.075], rad_length=15/4), 
           ThinMultipole('sb1_3', position=13.5, knl=[0.075], rad_length=15/4), 
           DipoleEdge('sb1_edge_exit', position=15.0, h=0.02, side='exit')]

    for idx, el in enumerate(ref):
        assert el == sliced_element[idx]       


def test_teapot_slice_Sbend_3_slices():
    sb1 = Sbend('sb1', length=15.0, position=7.5, angle=0.30)
    sliced_element = sb1.slice_element(num_slices=3)
    
    ref = [DipoleEdge('sb1_edge_entrance', position=0.0, h=0.02, side='entrance'), 
           ThinMultipole('sb1_0', position=1.875, knl=[0.1], rad_length=15/3), 
           ThinMultipole('sb1_1', position=7.5, knl=[0.1], rad_length=15/3), 
           ThinMultipole('sb1_2', position=13.125, knl=[0.1], rad_length=15/3), 
           DipoleEdge('sb1_edge_exit', position=15.0, h=0.02, side='exit')]

    for idx, el in enumerate(ref):
        assert el == sliced_element[idx]     

# OLD TEST, SHOULD BE UPDATED
# @mark.parametrize('name, nslices, length, delta, distance',
#                  [('el1_2', 2,  1.0, 1/6, 2/3),
#                   ('el1_3', 3,  1.0, 1/8, 3/8),
#                   ('el1_4', 4,  1.0, 1/10, 4/15),
#                   ('el1_5', 5,  1.0, 1/12, 5/24),
#                   ('el2_2', 2,  3.4, 3.4*1/6, 3.4*2/3),
#                   ('el2_3', 3,  3.4, 3.4*1/8, 3.4*3/8),
#                   ('el2_4', 4,  3.4, 3.4*1/10, 3.4*4/15),
#                   ('el2_5', 5,  3.4, 3.4*1/12, 3.4*5/24)])
# def test_teapot_slice_distances(name, nslices, length, delta, distance):
#     el = Element(name, length=length)
#     dl, dis = el.teapot_slicing(nslices)
#     errors = []
#     if not math.isclose(delta, dl, abs_tol=1e-15):
#         errors.append(f"Error: TEAPOT delta not correct, should be {delta}")
#     if not math.isclose(distance, dis, abs_tol=1e-15):
#         errors.append(f"Error: TEAPOT distance not correct, should be {distance}")
#     assert not errors, "errors occured:\n{}".format("\n".join(errors))
