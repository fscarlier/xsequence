"""
Module conversion_utils.cpymad_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module with functions for importing and exporting elements from and to cpymad
"""

ATTRIBUTE_MAP = {
                'length': 'l', 
                'location': 'at', 
                'reference': 'from', 
                'angle': 'angle',
                'tilt': 'tilt', 
                'k0': 'k0', 
                'e1': 'e1', 
                'e2': 'e2', 
                'polarity': 'polarity', 
                'ks': 'ks', 
                'k1': 'k1', 
                'k1s': 'k1s', 
                'k2': 'k2', 
                'k2s': 'k2s', 
                'k3': 'k3', 
                'k3s': 'k3s', 
                'knl': 'knl', 
                'ksl': 'ksl', 
                'voltage': 'volt', 
                'frequency': 'freq', 
                'lag': 'lag', 
                'hkick': 'hkick', 
                'vkick': 'vkick', 
                'kick': 'kick', 
                'mech_sep': 'mech_sep', 
                'slot_id': 'slot_id', 
                'assembly': 'assembly_id', 
                'kmax': 'kmax', 
                'kmin': 'kmin', 
                'calibration': 'calib',
                'aperture_size':'aperture',
                'aperture_type':'aper_type',
                }

INVERT_ATTRIBUTE_MAP = {v: k for k, v in ATTRIBUTE_MAP.items()}


MARKER_ATTR      = ['length', 'location', 'reference', 'slot_id', 'assembly', 'mech_sep']
RECTANGULARBEND_ATTR       = ['length', 'location', 'reference', 'polarity', 'angle', 'e1', 'e2', 'k0', 'mech_sep', 'slot_id', 'kmax', 'kmin', 'calibration', 'assembly']
SBEND_ATTR       = ['length', 'location', 'reference', 'polarity', 'angle', 'e1', 'e2', 'k0', 'mech_sep', 'slot_id', 'assembly']
SOLENOID_ATTR    = ['length', 'location', 'reference', 'ks', 'slot_id', 'mech_sep', 'assembly']
DRIFT_ATTR       = ['length', 'location', 'reference', 'slot_id', 'mech_sep', 'assembly']
COLLIMATOR_ATTR  = ['length', 'location', 'reference', 'slot_id', 'mech_sep', 'assembly']
PLACEHOLDER_ATTR = ['length', 'location', 'reference', 'slot_id', 'mech_sep', 'assembly']
INSTRUMENT_ATTR  = ['length', 'location', 'reference', 'slot_id', 'mech_sep', 'assembly']
MONITOR_ATTR     = ['length', 'location', 'reference', 'slot_id', 'mech_sep', 'assembly']
QUADRUPOLE_ATTR  = ['length', 'location', 'reference', 'polarity', 'k1', 'k1s', 'mech_sep', 'slot_id', 'assembly', 'kmax', 'kmin', 'calibration']
SEXTUPOLE_ATTR   = ['length', 'location', 'reference', 'polarity', 'k2', 'k2s', 'mech_sep', 'slot_id', 'assembly', 'kmax', 'kmin', 'calibration']
OCTUPOLE_ATTR    = ['length', 'location', 'reference', 'polarity', 'k3', 'k3s', 'mech_sep', 'slot_id', 'assembly', 'kmax', 'kmin', 'calibration']
MULTIPOLE_ATTR   = ['length', 'location', 'reference', 'polarity', 'knl', 'slot_id', 'assembly', 'mech_sep', 'ksl']
HKICKER_ATTR     = ['length', 'location', 'reference', 'polarity', 'kick', 'slot_id', 'assembly', 'mech_sep', 'kmax', 'kmin', 'calibration', 'tilt']
VKICKER_ATTR     = ['length', 'location', 'reference', 'polarity', 'kick', 'slot_id', 'assembly', 'mech_sep', 'kmax', 'kmin', 'calibration', 'tilt']
TKICKER_ATTR     = ['length', 'location', 'reference', 'polarity', 'hkick', 'vkick', 'slot_id', 'assembly', 'mech_sep']
RFCAVITY_ATTR    = ['length', 'location', 'reference', 'voltage', 'lag', 'mech_sep', 'slot_id', 'assembly']


CPYMAD_ELEMENT_DICT = {'marker': MARKER_ATTR         ,     
                       'drift': DRIFT_ATTR           ,   
                       'monitor': DRIFT_ATTR           ,   
                       'sbend': SBEND_ATTR           ,   
                       'rbend': RECTANGULARBEND_ATTR           ,   
                       'quadrupole': QUADRUPOLE_ATTR ,      
                       'sextupole': SEXTUPOLE_ATTR   ,  
                       'octupole': OCTUPOLE_ATTR     ,
                       'collimator': COLLIMATOR_ATTR ,    
                       'rfcavity': RFCAVITY_ATTR     ,
                       'multipole': MULTIPOLE_ATTR}


ELEMENT_DICT = {
                'Marker'     : [ATTRIBUTE_MAP[k] for k in MARKER_ATTR     ],   
                'RectangularBend'      : [ATTRIBUTE_MAP[k] for k in RECTANGULARBEND_ATTR      ],  
                'SectorBend'      : [ATTRIBUTE_MAP[k] for k in SBEND_ATTR      ],  
                'Solenoid'   : [ATTRIBUTE_MAP[k] for k in SOLENOID_ATTR   ],  
                'Drift'      : [ATTRIBUTE_MAP[k] for k in DRIFT_ATTR      ],  
                'Collimator' : [ATTRIBUTE_MAP[k] for k in COLLIMATOR_ATTR ],  
                'Placeholder': [ATTRIBUTE_MAP[k] for k in PLACEHOLDER_ATTR],  
                'Instrument' : [ATTRIBUTE_MAP[k] for k in INSTRUMENT_ATTR ],  
                'Monitor'    : [ATTRIBUTE_MAP[k] for k in MONITOR_ATTR    ],  
                'Quadrupole' : [ATTRIBUTE_MAP[k] for k in QUADRUPOLE_ATTR ],  
                'Sextupole'  : [ATTRIBUTE_MAP[k] for k in SEXTUPOLE_ATTR  ],  
                'Octupole'   : [ATTRIBUTE_MAP[k] for k in OCTUPOLE_ATTR   ],  
                'Multipole'  : [ATTRIBUTE_MAP[k] for k in MULTIPOLE_ATTR  ],  
                'Hkicker'    : [ATTRIBUTE_MAP[k] for k in HKICKER_ATTR    ],  
                'Vkicker'    : [ATTRIBUTE_MAP[k] for k in VKICKER_ATTR    ],  
                'Tkicker'    : [ATTRIBUTE_MAP[k] for k in TKICKER_ATTR    ],  
                'RFCavity'   : [ATTRIBUTE_MAP[k] for k in RFCAVITY_ATTR   ],  
                }


class AttributeMappingFromCpymad:
    def __init__(self, cpymad_element, attr_dict):
        for key in attr_dict:
            try: setattr(self, key, cpymad_element[ATTRIBUTE_MAP[key]]) 
            except: AttributeError
        
        try: self.frequency *= 1e6
        except: AttributeError
        try: self.voltage *= 1e6
        except: AttributeError


class AttributeMappingToCpymad:
    def __init__(self, element, attr_dict):
        self.params = {}
        for key in attr_dict:
            try: self.params[key] = element[INVERT_ATTRIBUTE_MAP[key]] 
            except: AttributeError
        
        try: self.params['freq'] /= 1e6
        except: AttributeError
        try: self.params['volt'] /= 1e6
        except: AttributeError


def from_cpymad(xs_cls, cpymad_element, name=None, aperture=False):
    if not isinstance(cpymad_element, dict):
        name = cpymad_element.name
        elemdata={'base_type':cpymad_element.base_type.name}
        for parname, par in cpymad_element.cmdpar.items():
            elemdata[parname]=par.value
        cpymad_element = elemdata
    attribute_list = CPYMAD_ELEMENT_DICT[cpymad_element['base_type']]
    if aperture:
        attribute_list.extend(['aperture_type', 'aperture_size'])
    mapped_attr = AttributeMappingFromCpymad(cpymad_element, attribute_list)
    return convert_element_from_cpymad(xs_cls, name, mapped_attr, attribute_list)


def convert_element_from_cpymad(xs_cls, name, mapped_attr, attribute_list):
    attribute_list = attribute_list.copy()
    kwargs = {}
    for key in attribute_list:
        try: kwargs[key] = getattr(mapped_attr, key)
        except: AttributeError
    return xs_cls(name, **kwargs)


def to_cpymad(element, madx):
    attribute_list = ELEMENT_DICT[element.__class__.__name__]
    mapped_attr = AttributeMappingToCpymad(element, attribute_list)
    base_type = element.__class__.__name__
    madx_base_type = base_type.lower()
    if base_type == 'RectangularBend':
        mapped_attr.params['l'] =element._chord_length
        mapped_attr.params['e1'] = element._rbend_e1
        mapped_attr.params['e2'] = element._rbend_e2
        madx_base_type = 'rbend'
    return convert_element_to_cpymad(madx_base_type, madx, element.name, mapped_attr, attribute_list)


def convert_element_to_cpymad(base_type, madx, name, mapped_attr, attribute_list):
    attribute_list = attribute_list.copy()
    kwargs = {}
    for key in attribute_list:
        try: kwargs[key] = mapped_attr.params[key]
        except: AttributeError
    madx.command[base_type].clone(name, **kwargs)


