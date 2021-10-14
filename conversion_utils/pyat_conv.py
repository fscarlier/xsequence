"""
Module conversion_utils.pyat_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module with functions for importing and exporting elements from and to pyat

Part I: Import functions

Part II: Export functions
"""

import at
import numpy as np
from scipy.special import factorial

FACTORIAL = factorial(np.arange(21), exact=True)

"""
Part I: Import functions
"""


def get_aperture_kwarg_from_pyat(pyat_element):
    aper_kwarg = {}
    try:
        if len(pyat_element.aperture) == 1 and pyat_element.aperture[0] == 0: 
            aper_kwarg = {}
        elif len(pyat_element.aperture) == 2:
            if pyat_element.aperture[0] == 0 or pyat_element.aperture[1] == 0: 
                aper_kwarg = {}
        else: 
            if pyat_element.apertype == 'circle':
                aper_kwarg = {'EApertures':[pyat_element.aperture[0], pyat_element.aperture[0]]}
            elif pyat_element.apertype == 'ellipse':
                aper_kwarg = {'EApertures':[pyat_element.aperture[0], pyat_element.aperture[1]]}
            elif pyat_element.apertype == 'rectangle':
                aper_kwarg = {'RApertures':[-pyat_element.aperture[0], pyat_element.aperture[0], 
                                            -pyat_element.aperture[1], pyat_element.aperture[1]]}
    except AttributeError:
        pass
    return aper_kwarg


def get_element_kwargs_from_pyat(pyat_element, attr_dict):
    # aper_kwarg = get_aperture_kwarg_from_pyat(pyat_element)
    aper_kwarg = {}
    kwargs = {}
    for key in attr_dict.keys():
        if key == 'kn':
            kwargs[key] = convert_PolyB_to_kn(pyat_element)
        elif key == 'ks':
            kwargs[key] = convert_PolyA_to_ks(pyat_element)
        else:
            try: kwargs[key] = getattr(pyat_element, attr_dict[key])
            except: AttributeError
    kwargs.update(aper_kwarg)
    return kwargs


def convert_PolyB_to_kn(pyat_element):
    try: return pyat_element.PolynomB*FACTORIAL[:len(pyat_element.PolynomB)]
    except: AttributeError


def convert_PolyA_to_ks(pyat_element):
    try: return pyat_element.PolynomA*FACTORIAL[:len(pyat_element.PolynomA)]
    except: AttributeError


def marker_from_pyat(el_class, pyat_element):
    return el_class(pyat_element.FamName)


def drift_from_pyat(el_class, pyat_element):
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 'int_steps':'NumIntSteps'}
    kwargs = get_element_kwargs_from_pyat(pyat_element, attr_dict)
    return el_class(pyat_element.FamName, **kwargs)


def sbend_from_pyat(el_class, pyat_element):
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 'int_steps':'NumIntSteps',
                'angle':'BendingAngle', 'e1':'EntranceAngle', 'e2':'ExitAngle'}
    kwargs = get_element_kwargs_from_pyat(pyat_element, attr_dict)
    return el_class(pyat_element.FamName, **kwargs)


def quadrupole_from_pyat(el_class, pyat_element):
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 
                'int_steps':'NumIntSteps', 'kn':'PolynomB', 'ks':'PolynomA'}
    kwargs = get_element_kwargs_from_pyat(pyat_element, attr_dict)
    return el_class(pyat_element.FamName, **kwargs)


def sextupole_from_pyat(el_class, pyat_element):
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 
                'int_steps':'NumIntSteps', 'kn':'PolynomB', 'ks':'PolynomA'}
    kwargs = get_element_kwargs_from_pyat(pyat_element, attr_dict)
    return el_class(pyat_element.FamName, **kwargs)


def octupole_from_pyat(el_class, pyat_element):
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 
                'int_steps':'NumIntSteps', 'kn':'PolynomB', 'ks':'PolynomA'}
    kwargs = get_element_kwargs_from_pyat(pyat_element, attr_dict)
    return el_class(pyat_element.FamName, **kwargs)


def collimator_from_pyat(el_class, pyat_element):
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 'int_steps':'NumIntSteps'}
    kwargs = get_element_kwargs_from_pyat(pyat_element, attr_dict)
    return el_class(pyat_element.FamName, **kwargs)


def rfcavity_from_pyat(el_class, pyat_element):
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 'int_steps':'NumIntSteps', 
                'volt':'Voltage', 'freq':'Frequency', 'harmonic_number':'HarmNumber', 'energy':'Energy'}
    kwargs = get_element_kwargs_from_pyat(pyat_element, attr_dict)
    return el_class(pyat_element.FamName, **kwargs)


FROM_PYAT_CONV = {'Marker' : marker_from_pyat,
                  'Drift' : drift_from_pyat,
                  'Dipole' : sbend_from_pyat,
                  'Quadrupole' : quadrupole_from_pyat, 
                  'Sextupole' : sextupole_from_pyat, 
                  'Octupole' : octupole_from_pyat, 
                  'Collimator' : collimator_from_pyat, 
                  'RFCavity' : rfcavity_from_pyat}


def convert_element_from_pyat(el_class, pyat_element):
    return FROM_PYAT_CONV[pyat_element.__class__.__name__](el_class, pyat_element)


"""
Part II: Export functions
"""


def get_aperture_kwarg_to_pyat(fsf_element):
    aper_kwarg = {}
    try:
        if len(fsf_element.aperture) == 1 and fsf_element.aperture[0] == 0: 
            aper_kwarg = {}
        elif len(fsf_element.aperture) == 2:
            if fsf_element.aperture[0] == 0 or fsf_element.aperture[1] == 0: 
                aper_kwarg = {}
        else: 
            if fsf_element.apertype == 'circle':
                aper_kwarg = {'EApertures':[fsf_element.aperture[0], fsf_element.aperture[0]]}
            elif fsf_element.apertype == 'ellipse':
                aper_kwarg = {'EApertures':[fsf_element.aperture[0], fsf_element.aperture[1]]}
            elif fsf_element.apertype == 'rectangle':
                aper_kwarg = {'RApertures':[-fsf_element.aperture[0], fsf_element.aperture[0], 
                                            -fsf_element.aperture[1], fsf_element.aperture[1]]}
    except AttributeError:
        pass
    return aper_kwarg


def convert_ks_to_polynomA(fsf_element):
    try: return fsf_element.ks/FACTORIAL[:len(fsf_element.ks)]
    except: AttributeError

def convert_kn_to_polynomB(fsf_element):
    try: return fsf_element.kn/FACTORIAL[:len(fsf_element.kn)]
    except: AttributeError


def get_element_kwargs_to_pyat(fsf_element, attr_dict):
    aper_kwarg = get_aperture_kwarg_to_pyat(fsf_element)
    kwargs = {}
    for key in attr_dict.keys():
        if key == 'PolynomB':
            kwargs[key] = convert_kn_to_polynomB(fsf_element)
        elif key == 'PolynomA':
            kwargs[key] = convert_ks_to_polynomA(fsf_element)
        else:
            try: kwargs[key] = getattr(fsf_element, attr_dict[key])
            except: AttributeError
    kwargs.update(aper_kwarg)
    return kwargs


def marker_to_pyat(fsf_element):
    return at.elements.Marker(fsf_element.name)
    

def drift_to_pyat(fsf_element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'int_steps', }
    kwargs = get_element_kwargs_to_pyat(fsf_element, attr_dict)
    return at.elements.Drift(fsf_element.name, fsf_element.length, **kwargs)
    

def sbend_to_pyat(fsf_element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'int_steps', 
                 'BendingAngle':'angle', 'EntranceAngle':'e1', 'ExitAngle':'e2'}
    kwargs = get_element_kwargs_to_pyat(fsf_element, attr_dict)
    return at.elements.Dipole(fsf_element.name, fsf_element.length, **kwargs)
 
 
def quadrupole_to_pyat(fsf_element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'int_steps', 'PolynomB':'kn', 'PolynomA':'ks'}
    kwargs = get_element_kwargs_to_pyat(fsf_element, attr_dict)
    return at.elements.Quadrupole(fsf_element.name, fsf_element.length, **kwargs)


def sextupole_to_pyat(fsf_element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'int_steps', 'PolynomB':'kn', 'PolynomA':'ks'}
    kwargs = get_element_kwargs_to_pyat(fsf_element, attr_dict)
    return at.elements.Sextupole(fsf_element.name, fsf_element.length, **kwargs)


def octupole_to_pyat(fsf_element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'int_steps', 'PolynomB':'kn', 'PolynomA':'ks'}
    kwargs = get_element_kwargs_to_pyat(fsf_element, attr_dict)
    return at.elements.Octupole(fsf_element.name, fsf_element.length, **kwargs)


def collimator_to_pyat(fsf_element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'int_steps', }
    kwargs = get_element_kwargs_to_pyat(fsf_element, attr_dict)
    return at.elements.Collimator(fsf_element.name, fsf_element.length, **kwargs)


def rfcavity_to_pyat(fsf_element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'int_steps', 'PolynomB':'knl', 'PolynomA':'ksl'}
    kwargs = get_element_kwargs_to_pyat(fsf_element, attr_dict)
    return at.elements.RFCavity(fsf_element.name, fsf_element.length, fsf_element.volt*1e6, fsf_element.freq*1e6, 
                                fsf_element.harmonic_number, fsf_element.energy*1e9, **kwargs)


def convert_element_to_pyat(fsf_element):
    return TO_PYAT_CONV[fsf_element.__class__.__name__](fsf_element)


TO_PYAT_CONV = {'Marker': marker_to_pyat, 
                'Drift':  drift_to_pyat, 
                'Sbend':  sbend_to_pyat, 
                'Rbend':  sbend_to_pyat, 
                'Quadrupole': quadrupole_to_pyat, 
                'Sextupole': sextupole_to_pyat, 
                'Collimator': collimator_to_pyat, 
                'RFCavity': rfcavity_to_pyat}
