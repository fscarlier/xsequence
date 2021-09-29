"""
Functions for importing and exporting elements from and to cpymad

Part I: Import functions

Part II: Export functions
"""

import fsf.elements 

"""
Part I: Import functions
"""


def get_element_kwargs_from_cpymad(cpymad_element, attr_dict):
    aper_dict = {'aper_type':'apertype', 'aperture':'aperture'}
    if cpymad_element.aperture != [0]:
        attr_dict.update(aper_dict)
    
    kwargs = {}
    for key in attr_dict.keys():
        try: kwargs[key] = getattr(cpymad_element, attr_dict[key])
        except: AttributeError
    return kwargs


def marker_from_cpymad(el_class, cpymad_element):
    attr_dict = {'position':'at'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def drift_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def sbend_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at', 'angle':'angle', 'e1':'e1', 'e2':'e2'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def rbend_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at', 'angle':'angle', 'e1':'e1', 'e2':'e2'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def quadrupole_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at', 'k1':'k1', 'k1s':'k1s'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def sextupole_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at', 'k2':'k2', 'k2s':'k2s'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def octupole_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at', 'k3':'k3', 'k3s':'k3s'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def collimator_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def rfcavity_from_cpymad(el_class, cpymad_element):
    attr_dict = {'length':'l', 'position':'at', 'freq':'freq', 'volt':'volt'}
    kwargs = get_element_kwargs_from_cpymad(cpymad_element, attr_dict)
    return el_class(cpymad_element.name, **kwargs)


def convert_element_from_cpymad(el_class, cpymad_element):
    return FROM_CPYMAD_CONV[cpymad_element.base_type.name](el_class, cpymad_element)


FROM_CPYMAD_CONV = {'marker' : marker_from_cpymad,
                    'drift' : drift_from_cpymad,
                    'sbend' : sbend_from_cpymad,
                    'rbend' : rbend_from_cpymad,
                    'quadrupole' : quadrupole_from_cpymad, 
                    'sextupole' : sextupole_from_cpymad, 
                    'octupole' : octupole_from_cpymad, 
                    'collimator' : collimator_from_cpymad, 
                    'rfcavity' : rfcavity_from_cpymad}


"""
Part II: Export functions
"""


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
    attr_dict = {'l':'length', 'at':'position', 'angle':'angle', 'e1':'e1', 'e2':'e2'}
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
    attr_dict = {'l':'length', 'at':'position', 'freq':'freq', 'volt':'volt'}
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