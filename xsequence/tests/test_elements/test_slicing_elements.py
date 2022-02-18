"""
Module tests.test_elements.test_slicing_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a test module to test correct slicing of elements.
"""

from xsequence.elements import *
from xsequence.slicing import get_teapot_slicing_positions
from xsequence.slicing import get_uniform_slicing_positions


"""TEST TEAPOT SLICING DITANCES"""

def test_teapot_slicing_default_1_slices():
    el = BaseElement('el', length=15.0)
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [0.0] 
    assert sliced_locations == slice_true_locations


def test_teapot_slicing_1_slices_defined_later():
    el = BaseElement('el', length=15.0)
    el.num_slices = 1
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [0.0] 
    assert sliced_locations == slice_true_locations


def test_teapot_slicing_4_slices_defined_later():
    el = BaseElement('el', length=15.0)
    el.num_slices = 4
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [-6.0, -2.0, 2.0, 6.0] 
    assert sliced_locations == slice_true_locations


def test_teapot_slicing_3_slices_defined_later():
    el = BaseElement('el', length=15.0)
    el.num_slices = 3
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [-5.625, 0.0, 5.625] 
    assert sliced_locations == slice_true_locations


def test_teapot_slicing_4_slices():
    el = BaseElement('el', length=15.0, num_slices=4)
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [-6.0, -2.0, 2.0, 6.0] 
    assert sliced_locations == slice_true_locations


def test_teapot_slicing_3_slices():
    el = BaseElement('el', length=15.0, num_slices=3)
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [-5.625, 0.0, 5.625] 
    assert sliced_locations == slice_true_locations


def test_teapot_slicing_4_slices_Quadrupole():
    el = Quadrupole('el', length=15.0, num_slices=4, k1=1.2)
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [-6.0, -2.0, 2.0, 6.0] 
    assert sliced_locations == slice_true_locations


def test_teapot_slicing_3_slices_Quadrupole():
    el = Quadrupole('el', length=15.0, num_slices=3, k1s=1.2)
    sliced_locations = get_teapot_slicing_positions(el)
    slice_true_locations = [-5.625, 0.0, 5.625] 
    assert sliced_locations == slice_true_locations


"""TEST UNIFORM SLICING DITANCES"""

def test_uniform_slicing_default_1_slices():
    el = BaseElement('el', length=15.0)
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [0.0] 
    assert sliced_locations == slice_true_locations


def test_uniform_slicing_1_slices_defined_later():
    el = BaseElement('el', length=15.0)
    el.num_slices = 1
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [0.0] 
    assert sliced_locations == slice_true_locations


def test_uniform_slicing_4_slices_defined_later():
    el = BaseElement('el', length=15.0)
    el.num_slices = 4
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [-7.5, -2.5, 2.5, 7.5] 
    assert sliced_locations == slice_true_locations


def test_uniform_slicing_3_slices_defined_later():
    el = BaseElement('el', length=15.0)
    el.num_slices = 3
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [-7.5, 0.0, 7.5] 
    assert sliced_locations == slice_true_locations


def test_uniform_slicing_4_slices():
    el = BaseElement('el', length=15.0, num_slices=4)
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [-7.5, -2.5, 2.5, 7.5] 
    assert sliced_locations == slice_true_locations


def test_uniform_slicing_3_slices():
    el = BaseElement('el', length=15.0, num_slices=3)
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [-7.5, 0.0, 7.5] 
    assert sliced_locations == slice_true_locations


def test_uniform_slicing_4_slices_Quadrupole():
    el = Quadrupole('el', length=15.0, num_slices=4, k1=1.2)
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [-7.5, -2.5, 2.5, 7.5] 
    assert sliced_locations == slice_true_locations


def test_uniform_slicing_3_slices_Quadrupole():
    el = Quadrupole('el', length=15.0, num_slices=3, k1s=1.2)
    sliced_locations = get_uniform_slicing_positions(el)
    slice_true_locations = [-7.5, 0.0, 7.5] 
    assert sliced_locations == slice_true_locations


"""TEST THIN EQUIVALENT FROM ELEMENT CLASSES"""

def test_sliced_element_Sextupole_4():
    el = Sextupole('el', length=15.0, k2=0.40, num_slices=4)
    sliced_element = el._get_thin_element()
    true_element_slice = ThinMultipole('el', knl=[0.0, 0.0, 15*0.4/4, 0.0], radiation_length=15/4) 
    assert sliced_element == true_element_slice       


def test_sliced_element_Sextupole_5():
    el = Sextupole('el', length=15.0, k2=0.40, num_slices=5)
    sliced_element = el._get_thin_element()
    true_element_slice = ThinMultipole('el', knl=[0.0, 0.0, 15*0.4/5, 0.0], radiation_length=15/5) 
    assert sliced_element == true_element_slice       


def test_sliced_element_Quadrupole_4():
    el = Quadrupole('el', length=15.0, k1=0.40, num_slices=4)
    sliced_element = el._get_thin_element()
    true_element_slice = ThinMultipole('el', knl=[0.0, 15*0.4/4, 0.0, 0.0], radiation_length=15/4) 
    assert sliced_element == true_element_slice       


def test_sliced_element_Quadrupole_5():
    el = Quadrupole('el', length=15.0, k1=0.40, num_slices=5)
    sliced_element = el._get_thin_element()
    true_element_slice = ThinMultipole('el', knl=[0.0, 15*0.4/5, 0.0, 0.0], radiation_length=15/5) 
    assert sliced_element == true_element_slice       


def test_sliced_element_Sbend():
    el = SectorBend('el', length=15.0, angle=0.30, num_slices=4)
    sliced_element = el._get_thin_element()
    true_element_slice = ThinMultipole('el', knl=[0.075], radiation_length=15/4)
    assert sliced_element == true_element_slice       
