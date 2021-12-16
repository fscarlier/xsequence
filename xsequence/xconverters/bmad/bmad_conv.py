"""
Module conversion_utils.bmad_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module with functions for importing and exporting elements from and to bmad
"""


from xsequence.xconverters.bmad import bmad_properties

class ElementNotDefinedYet(Exception):
    """ Element conversion is not yet defined for this element type"""
    def __init__(self, element_name:str, base_type:str) -> None:
        self.element = element_name 
        self.base_type = base_type
        print(f"Element conversion not defined yet for base type: {self.base_type} at element: {self.element}")


def get_element_string_definition(name, bmad_base_type, attributes):
    if attributes:
        attribute_str = ', '.join(f'{key} = {val}' for (key, val) in attributes.items())
        element_str = f'{name}: {bmad_base_type}, {attribute_str}'
    else:
        element_str = f'{name}: {bmad_base_type}'
    return element_str


def to_bmad_str(element):
    bmad_base_type = bmad_properties.base_types[element.__class__.__name__]
    attributes = {}

    if bmad_base_type == 'marker':
        pass
    elif bmad_base_type == 'drift':
        attributes['l'] = element.length
    elif bmad_base_type == 'rbend':
        bmad_base_type = 'sbend'
        attributes['l'] = element.length
        attributes['angle'] = element.angle
        attributes['e1'] = element.e1
        attributes['e2'] = element.e2
        # attributes['angle'] = element.angle
        # attributes['l'] = element._chord_length
        # attributes['e1'] = element._rbend_e1
        # attributes['e2'] = element._rbend_e2
    elif bmad_base_type == 'sbend':
        attributes['l'] = element.length
        attributes['angle'] = element.angle
        attributes['e1'] = element.e1
        attributes['e2'] = element.e2
    elif bmad_base_type == 'quadrupole':
        attributes['l'] = element.length
        attributes['k1'] = element.k1
    elif bmad_base_type == 'sextupole':
        attributes['l'] = element.length
        attributes['k2'] = element.k2
    elif bmad_base_type == 'octupole':
        attributes['l'] = element.length
        attributes['k3'] = element.k3
    elif bmad_base_type == 'rfcavity':
        attributes['l'] = element.length
        attributes['voltage'] = element.voltage
        attributes['rf_frequency'] = element.frequency
        attributes['phi0'] = element.lag + 0.5
    else:
        raise ElementNotDefinedYet(element_name=element.name, base_type=bmad_base_type)

    if "$" in element.name:
        el_name = element.name.replace("$", "")
    else:
        el_name = element.name

    return get_element_string_definition(el_name, bmad_base_type, attributes)

