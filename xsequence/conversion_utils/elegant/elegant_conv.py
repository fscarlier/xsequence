"""
Module conversion_utils.elegant_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module with functions for exporting elements to elegant
"""
import xsequence.conversion_utils.elegant.elegant_properties as elegant_properties


def convert_element_dict_to_elegant_definition(base_type: str, el_dict:dict) -> str:
    return elegant_properties.CONVERT_ELEMENT_DICT[base_type.lower()](el_dict)

def to_elegant(element) -> list[str, dict, str]:
    base_type = element.__class__.__name__
    el_dict = element.get_dict()
    elegant_definition= convert_element_dict_to_elegant_definition(base_type, el_dict)

    return el_dict['name'], el_dict, elegant_definition
