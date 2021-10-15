"""
Module conversion_utils.cpymad_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module with functions for importing and exporting elements from and to cpymad
"""

ATTRITUBTE_MAPPING = {'length':'l', 
                      'position':'at', 
                      'angle':'angle', 
                      'e1':'e1', 
                      'e2':'e2', 
                      'k1':'k1', 
                      'k1s':'k1s', 
                      'k2':'k2', 
                      'k2s':'k2s', 
                      'k3':'k3', 
                      'k3s':'k3s', 
                      'knl':'knl', 
                      'ksl':'ksl', 
                      'freq':'freq', 
                      'volt':'volt', 
                      'lag':'lag',
                      'aper_type':'apertype', 
                      'aperture':'aperture'}

MARKER_ATTR     = ['position']
DRIFT_ATTR      = ['length', 'position', 'aper_type', 'aperture']
COLLIMATOR_ATTR = ['length', 'position', 'aper_type', 'aperture']
SBEND_ATTR      = ['length', 'position', 'angle', 'e1', 'e2', 'aper_type', 'aperture']
RBEND_ATTR      = ['length', 'position', 'angle', 'e1', 'e2', 'aper_type', 'aperture']
QUADRUPOLE_ATTR = ['length', 'position', 'k1', 'k1s', 'aper_type', 'aperture']
SEXTUPOLE_ATTR  = ['length', 'position', 'k2', 'k2s', 'aper_type', 'aperture']
OCTUPOLE_ATTR   = ['length', 'position', 'k3', 'k3s', 'aper_type', 'aperture']
MULTIPOLE_ATTR  = ['length', 'position', 'knl', 'ksl', 'aper_type', 'aperture']
RFCAVITY_ATTR   = ['length', 'position', 'freq', 'volt', 'lag', 'aper_type', 'aperture']
    

class ConvertElementFromCpymad:
    def __init__(self, xs_cls, cpymad_element):
        self.element = cpymad_element
        self.xs_cls = xs_cls
        attribute_list = self.choose_element_from_cpymad()
        self.convert_element_from_cpymad(attribute_list)
    
    def choose_element_from_cpymad(self): 
        base_type = self.element.base_type.name
        if base_type == 'marker':      
            attribute_list = MARKER_ATTR      
        if base_type == 'drift':       
            attribute_list = DRIFT_ATTR      
        if base_type == 'sbend':       
            attribute_list = SBEND_ATTR      
        if base_type == 'rbend':       
            attribute_list = RBEND_ATTR      
        if base_type == 'quadrupole':  
            attribute_list = QUADRUPOLE_ATTR      
        if base_type == 'sextupole':   
            attribute_list = SEXTUPOLE_ATTR      
        if base_type == 'octupole':    
            attribute_list = OCTUPOLE_ATTR      
        if base_type == 'collimator':  
            attribute_list = COLLIMATOR_ATTR      
        if base_type == 'rfcavity':    
            attribute_list = RFCAVITY_ATTR      
        if base_type == 'multipole':    
            attribute_list = MULTIPOLE_ATTR 
        return attribute_list     

    def convert_element_from_cpymad(self, attribute_list):
        if self.element.aperture == [0]:
            attribute_list.pop('aper_type', 'aperture')
        kwargs = {}
        for key in attribute_list:
            try: kwargs[key] = getattr(self.element, ATTRITUBTE_MAPPING[key])
            except: AttributeError
        return self.xs_cls(self.element.name, **kwargs)

    def get_element_kwargs_from_cpymad(self, attribute_list):
        if self.element.aperture == [0]:
            attribute_list.pop('aper_type', 'aperture')
        kwargs = {}
        for key in attribute_list:
            try: kwargs[key] = getattr(self.element, ATTRITUBTE_MAPPING[key])
            except: AttributeError
        return kwargs

    def element_from_cpymad(self, attribute):
        kwargs = self.get_element_kwargs_from_cpymad(MARKER_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def drift_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(DRIFT_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def sbend_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(SBEND_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def rbend_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(RBEND_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def quadrupole_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(QUADRUPOLE_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def sextupole_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(SEXTUPOLE_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def octupole_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(OCTUPOLE_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def collimator_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(COLLIMATOR_ATTR)
        return self.xs_cls(self.element.name, **kwargs)

    def rfcavity_from_cpymad(self):
        kwargs = self.get_element_kwargs_from_cpymad(RFCAVITY_ATTR)
        return self.xs_cls(self.element.name, **kwargs)




class ConvertElementFromCpymad:
    def __init__(self, xs_element, madx):
        self.element = xs_element
        self.madx = madx

    def convert_from_cpymad(self): 
        base_type = self.element.base_type.name
        if base_type == 'marker': 
            self.marker_to_cpymad()
        if base_type == 'drift': 
            self.drift_to_cpymad()
        if base_type == 'sbend': 
            self.sbend_to_cpymad()
        if base_type == 'rbend': 
            self.rbend_to_cpymad()
        if base_type == 'quadrupole': 
            self.quadrupole_to_cpymad() 
        if base_type == 'sextupole': 
            self.sextupole_to_cpymad() 
        if base_type == 'octupole': 
            self.octupole_to_cpymad() 
        if base_type == 'collimator': 
            self.collimator_to_cpymad() 
        if base_type == 'rfcavity': 
            self.rfcavity_to_cpymad()
    

    def get_element_kwargs_to_cpymad(fsf_element, attr_dict):
        aper_dict = {'apertype':'aper_type', 'aperture':'aperture'}
        try: 
            if fsf_element.aperture != [0]: attr_dict.update(aper_dict)
        except:AttributeError

        kwargs = {}
        for key in attr_dict.keys():
            try: kwargs[key] = getattr(fsf_element, attr_dict[key])
            except: AttributeError
        return kwargs


    def marker_to_cpymad(fsf_element, madx):
        attr_dict = {'at':'position'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def drift_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'length', 'at':'position'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def sbend_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'length', 'at':'position', 'angle':'angle', 'e1':'e1', 'e2':'e2'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def rbend_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'_chord_length', 'at':'position', 'angle':'angle', 'e1':'_rbend_e1', 'e2':'_rbend_e2'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def quadrupole_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'length', 'at':'position', 'k1':'k1', 'k1s':'k1s'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def sextupole_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'length', 'at':'position', 'k2':'k2', 'k2s':'k2s'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def octupole_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'length', 'at':'position', 'k3':'k3', 'k3s':'k3s'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def collimator_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'length', 'at':'position'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def rfcavity_to_cpymad(fsf_element, madx):
        attr_dict = {'l':'length', 'at':'position', 'freq':'freq', 'volt':'volt', 'lag':'lag'}
        kwargs = get_element_kwargs_to_cpymad(fsf_element, attr_dict)
        madx.command[fsf_element.__class__.__name__.lower()].clone(fsf_element.name, **kwargs)


    def convert_element_to_cpymad(fsf_element, madx):
        return TO_CPYMAD_CONV[fsf_element.__class__.__name__](fsf_element, madx)


    TO_CPYMAD_CONV = {'Marker' : marker_to_cpymad,
                    'Drift' : drift_to_cpymad,
                    'Sbend' : sbend_to_cpymad,
                    'Rbend' : rbend_to_cpymad,
                    'Quadrupole' : quadrupole_to_cpymad, 
                    'Sextupole' : sextupole_to_cpymad, 
                    'Octupole' : octupole_to_cpymad, 
                    'Collimator' : collimator_to_cpymad, 
                    'RFCavity' : rfcavity_to_cpymad}

    def marker_from_cpymad(xs_cls, cpymad_element):