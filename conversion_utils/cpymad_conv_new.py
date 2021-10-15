"""
Module conversion_utils.cpymad_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module with functions for importing and exporting elements from and to cpymad
"""

MARKER_ATTR     = ['position']
DRIFT_ATTR      = ['length', 'position', 'aperture_type', 'aperture_size']
COLLIMATOR_ATTR = ['length', 'position', 'aperture_type', 'aperture_size']
SBEND_ATTR      = ['length', 'position', 'angle', 'e1', 'e2', 'aperture_type', 'aperture_size']
RBEND_ATTR      = ['length', 'position', 'angle', 'e1', 'e2', 'aperture_type', 'aperture_size']
QUADRUPOLE_ATTR = ['length', 'position', 'k1', 'k1s', 'aperture_type', 'aperture_size']
SEXTUPOLE_ATTR  = ['length', 'position', 'k2', 'k2s', 'aperture_type', 'aperture_size']
OCTUPOLE_ATTR   = ['length', 'position', 'k3', 'k3s', 'aperture_type', 'aperture_size']
MULTIPOLE_ATTR  = ['length', 'position', 'knl', 'ksl', 'aperture_type', 'aperture_size']
RFCAVITY_ATTR   = ['length', 'position', 'frequency', 'voltage', 'lag', 'aperture_type', 'aperture_size']


CPYMAD_MARKER_ATTR     = ['at']
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


class ConvertElementFromCpymad(AttributeMappingFromCpymad):
    def __init__(self, xs_cls, cpymad_element):
        super().__init__(cpymad_element)
        self.element = cpymad_element
        self.xs_cls = xs_cls
        attribute_list = CPYMAD_ELEMENT_DICT[self.element.base_type.name]
        converted_element = self.convert_element_from_cpymad(attribute_list)
        ## Space here to adjust element or call new methods
        return converted_element
    
    def convert_element_from_cpymad(self, attribute_list):
        if self.aperture_size == [0]:
            attribute_list.pop('aperture_type', 'aperture_size')
        kwargs = {}
        for key in attribute_list:
            try: kwargs[key] = self.key
            except: AttributeError
        return self.xs_cls(self.element.name, **kwargs)


class ConvertElementToCpymad(AttributeMappingToCpymad):
    def __init__(self, element, madx):
        super().__init__(element)
        self.element = element
        self.madx = madx
        self.base_type = self.element.__class__.__name__
        attribute_list = ELEMENT_DICT[self.base_type]
        converted_element = self.convert_element_to_cpymad(attribute_list)
        ## Space here to adjust element or call new methods
        return converted_element
    
    def convert_element_to_cpymad(self, attribute_list):
        if self.aperture == [0]:
            attribute_list.pop('aper_type', 'aperture')
        kwargs = {}
        for key in attribute_list:
            try: kwargs[key] = self.key
            except: AttributeError
        self.madx.command[self.base_type.lower()].clone(self.element.name, **kwargs)