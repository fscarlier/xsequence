"""
Module conversion_utils.cpymad_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module with functions for importing and exporting elements from and to cpymad
"""

MARKER_ATTR     = ['position', 'aperture_type', 'aperture_size']
DRIFT_ATTR      = ['length', 'position', 'aperture_type', 'aperture_size']
COLLIMATOR_ATTR = ['length', 'position', 'aperture_type', 'aperture_size']
SBEND_ATTR      = ['length', 'position', 'angle', 'e1', 'e2', 'aperture_type', 'aperture_size']
RBEND_ATTR      = ['length', 'position', 'angle', 'e1', 'e2', 'aperture_type', 'aperture_size']
QUADRUPOLE_ATTR = ['length', 'position', 'k1', 'k1s', 'aperture_type', 'aperture_size']
SEXTUPOLE_ATTR  = ['length', 'position', 'k2', 'k2s', 'aperture_type', 'aperture_size']
OCTUPOLE_ATTR   = ['length', 'position', 'k3', 'k3s', 'aperture_type', 'aperture_size']
MULTIPOLE_ATTR  = ['length', 'position', 'knl', 'ksl', 'aperture_type', 'aperture_size']
RFCAVITY_ATTR   = ['length', 'position', 'frequency', 'voltage', 'lag', 'aperture_type', 'aperture_size']


CPYMAD_MARKER_ATTR     = ['at', 'aper_type', 'aperture']
CPYMAD_DRIFT_ATTR      = ['l', 'at', 'aper_type', 'aperture']
CPYMAD_COLLIMATOR_ATTR = ['l', 'at', 'aper_type', 'aperture']
CPYMAD_SBEND_ATTR      = ['l', 'at', 'angle', 'e1', 'e2', 'aper_type', 'aperture']
CPYMAD_RBEND_ATTR      = ['l', 'at', 'angle', 'e1', 'e2', 'aper_type', 'aperture']
CPYMAD_QUADRUPOLE_ATTR = ['l', 'at', 'k1', 'k1s', 'aper_type', 'aperture']
CPYMAD_SEXTUPOLE_ATTR  = ['l', 'at', 'k2', 'k2s', 'aper_type', 'aperture']
CPYMAD_OCTUPOLE_ATTR   = ['l', 'at', 'k3', 'k3s', 'aper_type', 'aperture']
CPYMAD_MULTIPOLE_ATTR  = ['l', 'at', 'knl', 'ksl', 'aper_type', 'aperture']
CPYMAD_RFCAVITY_ATTR   = ['l', 'at', 'freq', 'volt', 'lag', 'aper_type', 'aperture']


CPYMAD_ELEMENT_DICT = {'marker': MARKER_ATTR         ,     
                       'drift': DRIFT_ATTR           ,   
                       'sbend': SBEND_ATTR           ,   
                       'rbend': RBEND_ATTR           ,   
                       'quadrupole': QUADRUPOLE_ATTR ,      
                       'sextupole': SEXTUPOLE_ATTR   ,  
                       'octupole': OCTUPOLE_ATTR     ,
                       'collimator': COLLIMATOR_ATTR ,    
                       'rfcavity': RFCAVITY_ATTR     ,
                       'multipole': MULTIPOLE_ATTR}


ELEMENT_DICT = {'Marker': CPYMAD_MARKER_ATTR         ,     
                'Drift': CPYMAD_DRIFT_ATTR           ,   
                'Sbend': CPYMAD_SBEND_ATTR           ,   
                'Rbend': CPYMAD_RBEND_ATTR           ,   
                'Quadrupole': CPYMAD_QUADRUPOLE_ATTR ,      
                'Sextupole': CPYMAD_SEXTUPOLE_ATTR   ,  
                'Octupole': CPYMAD_OCTUPOLE_ATTR     ,
                'Collimator': CPYMAD_COLLIMATOR_ATTR ,    
                'RFCavity': CPYMAD_RFCAVITY_ATTR     ,
                'Multipole': CPYMAD_MULTIPOLE_ATTR}


class AttributeMappingFromCpymad:
    def __init__(self, cpymad_element):
        try: self.length = cpymad_element.l 
        except: AttributeError
        try: self.position = cpymad_element.at 
        except: AttributeError
        try: self.angle = cpymad_element.angle 
        except: AttributeError
        try: self.e1 = cpymad_element.e1 
        except: AttributeError
        try: self.e2 = cpymad_element.e2 
        except: AttributeError
        try: self.k1 = cpymad_element.k1 
        except: AttributeError
        try: self.k1s = cpymad_element.k1s 
        except: AttributeError
        try: self.k2 = cpymad_element.k2 
        except: AttributeError
        try: self.k2s = cpymad_element.k2s 
        except: AttributeError
        try: self.k3 = cpymad_element.k3 
        except: AttributeError
        try: self.k3s = cpymad_element.k3s 
        except: AttributeError
        try: self.knl = cpymad_element.knl 
        except: AttributeError
        try: self.ksl = cpymad_element.ksl 
        except: AttributeError
        try: self.frequency = cpymad_element.freq * 1e6
        except: AttributeError
        try: self.voltage = cpymad_element.volt * 1e6
        except: AttributeError
        try: self.lag = cpymad_element.lag
        except: AttributeError
        try: self.aperture_type = cpymad_element.apertype 
        except: AttributeError
        try: self.aperture_size = cpymad_element.aperture
        except: AttributeError


class AttributeMappingToCpymad:
    def __init__(self, element):
        try: self.l = element.length 
        except: AttributeError
        try: self.at = element.position 
        except: AttributeError
        try: self.angle = element.angle 
        except: AttributeError
        try: self.e1 = element.e1 
        except: AttributeError
        try: self.e2 = element.e2 
        except: AttributeError
        try: self.k1 = element.k1 
        except: AttributeError
        try: self.k1s = element.k1s 
        except: AttributeError
        try: self.k2 = element.k2 
        except: AttributeError
        try: self.k2s = element.k2s 
        except: AttributeError
        try: self.k3 = element.k3 
        except: AttributeError
        try: self.k3s = element.k3s 
        except: AttributeError
        try: self.knl = element.knl 
        except: AttributeError
        try: self.ksl = element.ksl 
        except: AttributeError
        try: self.freq = element.frequency / 1e6
        except: AttributeError
        try: self.volt = element.voltage / 1e6
        except: AttributeError
        try: self.lag = element.lag
        except: AttributeError
        try: self.apertype = element.aperture_type 
        except: AttributeError
        try: self.aperture = element.aperture_size
        except: AttributeError


def from_cpymad(xs_cls, cpymad_element):
    mapped_attr = AttributeMappingFromCpymad(cpymad_element)
    attribute_list = CPYMAD_ELEMENT_DICT[cpymad_element.base_type.name]
    return convert_element_from_cpymad(xs_cls, cpymad_element.name, mapped_attr, attribute_list)


def convert_element_from_cpymad(xs_cls, name, mapped_attr, attribute_list):
    attribute_list = attribute_list.copy()
    if mapped_attr.aperture_size == [0]:
        attribute_list.remove('aperture_type')
        attribute_list.remove('aperture_size')
    kwargs = {}
    for key in attribute_list:
        try: kwargs[key] = getattr(mapped_attr, key)
        except: AttributeError
    return xs_cls(name, **kwargs)


def to_cpymad(element, madx):
    mapped_attr = AttributeMappingToCpymad(element)
    base_type = element.__class__.__name__
    if base_type == 'Rbend':
        mapped_attr.l =element._chord_length
        mapped_attr.e1 = element._rbend_e1
        mapped_attr.e2 = element._rbend_e2
    
    attribute_list = ELEMENT_DICT[base_type]
    return convert_element_to_cpymad(base_type, madx, element.name, mapped_attr, attribute_list)


def convert_element_to_cpymad(base_type, madx, name, mapped_attr, attribute_list):
    attribute_list = attribute_list.copy()
    if not hasattr(mapped_attr, 'aperture_size'):
        attribute_list.remove('aper_type')
        attribute_list.remove('aperture')
    kwargs = {}
    for key in attribute_list:
        try: kwargs[key] = getattr(mapped_attr, key)
        except: AttributeError
    madx.command[base_type.lower()].clone(name, **kwargs)


