import at, copy
import numpy as np
from scipy.special import factorial
from fsf.conversion_utils import conv_utils
import fsf.elements_dataclasses as xed

FACTORIAL = factorial(np.arange(21), exact=True)

DIFF_ATTRIBUTE_MAP_PYAT = {
                             'length':'Length',
                             'angle':'BendingAngle',
                             'e1':'EntranceAngle',
                             'e2':'ExitAngle',
                             'kn':'PolynomB',
                             'ks':'PolynomA',
                             'voltage':'Voltage',
                             'frequency':'Frequency',
                             'harmonic_number':'HarmNumber',
                             'energy':'Energy',
                            }


DIFF_ATTRIBUTE_MAP_TO_PYAT = {
                             'length':'length',
                             'int_steps':'NumIntSteps',
                             'angle':'BendingAngle',
                             'e1':'EntranceAngle',
                             'e2':'ExitAngle',
                             'kn':'PolynomB',
                             'ks':'PolynomA',
                             'voltage':'voltage',
                             'frequency':'frequency',
                             'harmonic_number':'harmonic_number',
                             'energy':'energy',
                            }


def attr_mapping_from_pyat(pyat_element):
    element_kw = {}
    for key in DIFF_ATTRIBUTE_MAP_PYAT:
        try: element_kw[key] = pyat_element.pop(DIFF_ATTRIBUTE_MAP_PYAT[key]) 
        except: KeyError 
    
    if 'kn' in element_kw:
        element_kw['kn'] = element_kw['kn']*FACTORIAL[:len(element_kw['kn'])]
    
    if 'ks' in element_kw:
        element_kw['ks'] = element_kw['ks']*FACTORIAL[:len(element_kw['ks'])]

    if 'EApertures' in pyat_element:
        element_kw['aperture_data'] = xed.EllipticalAperture(aperture_size=pyat_element['EApertures'], 
                                                             aperture_type='ellipse') 
    if 'RApertures' in pyat_element:
        element_kw['aperture_data'] = xed.RectangularAperture(aperture_size=pyat_element['EApertures'], 
                                                             aperture_type='ellipse') 
    if 'NumIntSteps' in pyat_element or 'PassMethod' in pyat_element:
        element_kw['pyat_data'] = xed.PyatData(NumIntSteps=pyat_element.pop('NumIntSteps', None), PassMethod=pyat_element.pop('PassMethod', None))
    return element_kw


def from_pyat(xs_cls, pyat_element, name=None, aperture=False):
    if not isinstance(pyat_element, dict):
        name = pyat_element.FamName
        elemdata={'base_type':pyat_element.__class__.__name__}
        elemdata.update(dict(pyat_element.items()))
        pyat_element = elemdata
    
    mapped_attr = attr_mapping_from_pyat(pyat_element)
    
    if xs_cls.__name__ == 'Quadrupole':
        mapped_attr['k1'] = mapped_attr['kn'][1]
        mapped_attr['k1s'] = mapped_attr['ks'][1]
    if xs_cls.__name__ == 'Sextupole':
        mapped_attr['k2'] = mapped_attr['kn'][2]
        mapped_attr['k2s'] = mapped_attr['ks'][2]
    if xs_cls.__name__ == 'Octupole':
        mapped_attr['k3'] = mapped_attr['kn'][3]
        mapped_attr['k3s'] = mapped_attr['ks'][3]
    return xs_cls(name, **mapped_attr)


def attr_mapping_to_pyat(xe_element):
    pyat_element_kw = {}
    for key in DIFF_ATTRIBUTE_MAP_TO_PYAT:
        try: pyat_element_kw[DIFF_ATTRIBUTE_MAP_TO_PYAT[key]] = xe_element[key] 
        except: KeyError 
    
    if 'PolynomB' in pyat_element_kw:
        pyat_element_kw['PolynomB'] = pyat_element_kw['PolynomB']/FACTORIAL[:len(pyat_element_kw['PolynomB'])]
    
    if 'PolynomA' in pyat_element_kw:
        pyat_element_kw['PolynomA'] = pyat_element_kw['PolynomA']/FACTORIAL[:len(pyat_element_kw['PolynomA'])]

    return pyat_element_kw


def to_pyat(xe_element):
    element_dict = copy.copy(xe_element.get_dict())
    try: element_dict['kn'] = xe_element.strength_data.kn
    except: AttributeError
    try: element_dict['ks'] = xe_element.strength_data.ks
    except: AttributeError
    mapped_attr = attr_mapping_to_pyat(element_dict)

    if xe_element.aperture_data is not None: 
        if isinstance(xe_element.aperture_data, xed.EllipticalAperture):
            ### NOTE: aperture offsets not converted to pyat for elliptical apertures
            mapped_attr['EApertures'] = xe_element.aperture_data.aperture_size 
        elif isinstance(xe_element.aperture_data, xed.RectangularAperture):
            mapped_attr['RApertures'] = xe_element.aperture_data.get_4_array()
    
    try: 
        if xe_element.pyat_data.NumIntSteps is not None:
            mapped_attr['NumIntSteps'] = xe_element.pyat_data.NumIntSteps
    except: AttributeError
    try: 
        if xe_element.pyat_data.PassMethod is not None:
            mapped_attr['PassMethod'] = xe_element.pyat_data.PassMethod
    except: AttributeError
    
    if 'frequency' in mapped_attr:
        mapped_attr['energy'] = xe_element.rf_data.energy    
        mapped_attr['harmonic_number'] = xe_element.rf_data.harmonic_number    

    mapped_attr.update({'family_name':xe_element.name})
    if xe_element.__class__.__name__ == 'Octupole':
        mapped_attr['poly_a'] = mapped_attr.pop('PolynomA')
        mapped_attr['poly_b'] = mapped_attr.pop('PolynomB')

    return TO_PYAT_CONV[xe_element.__class__.__name__](**mapped_attr)


TO_PYAT_CONV = {'Marker': at.Marker, 
                'Drift':  at.Drift, 
                'SectorBend':  at.Dipole, 
                'RectangularBend':  at.Dipole, 
                'Quadrupole': at.Quadrupole, 
                'Sextupole': at.Sextupole, 
                'Octupole': at.Octupole, 
                'Collimator': at.Drift, 
                'RFCavity': at.RFCavity}

