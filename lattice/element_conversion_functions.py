import at 
import copy
import lattice.elements as lel


def convert_cpymad_element_to_fff(element):
    base_type = element.base_type.name
    return lel.CPYMAD_TO_FFF_MAP[base_type].from_cpymad(element)


def convert_pyat_element_to_fff(element):
    base_type = element.__class__.__name__
    return lel.PYAT_TO_FFF_MAP[base_type].from_pyat(element)


def from_cpymad(el_class, element):
    """ 
    Create specific Element instance from cpymad element
    
    Args:
        element: cpymad element instance
    """
    name = element.name.replace('.', '_').lower()
    if element == element.base_type:
        return el_class(name)
    else:
        kwargs_element = {k: v.value for k, v in element._data.items() if v.inform}
        # check if parent different then basetype
        if element.parent.name != element.base_type.name:
            kwargs = {k: v.value for k, v in element.parent._data.items() if v.inform}
            kwargs.update(kwargs_element)
        else:
            kwargs = kwargs_element
        
        try: kwargs['position'] = kwargs.pop('at')
        except KeyError: pass
        try: kwargs['length'] = kwargs.pop('l')
        except KeyError: pass
        kwargs['parent'] = element.parent.name
        return el_class(name, **kwargs)


def to_cpymad(element, madx):
    """ 
    Create cpymad element in madx instance from Element
    
    Args:
        element: fff Element instance
        madx: cpymad Madx() instance
    Returns:
        Updated Madx() instance
    """
    element_type = lel.FFF_TO_CPYMAD_MAP[element.__class__.__name__]
    kwargs = copy.copy(vars(element))
    kwargs['l'] = kwargs.pop('length')
    kwargs['at'] = kwargs.pop('pos')
    kwargs.pop('name')
    kwargs.pop('parent')
    
    kw = copy.copy(kwargs)
    for key in kw.keys():
        if key not in madx.elements[element_type].keys():
            kwargs.pop(key)
    if element_type == 'quadrupole':
        try: kwargs['k1'] = kwargs['knl'][1]
        except: KeyError
        try: kwargs['k1s'] = kwargs['ksl'][1]
        except: KeyError
    elif element_type == 'sextupole':
        try: kwargs['k2'] = kwargs['knl'][2]
        except: KeyError
        try: kwargs['k2s'] = kwargs['ksl'][2]
        except: KeyError
    elif element_type == 'octupole':
        try: kwargs['k3'] = kwargs['knl'][3]
        except: KeyError
        try: kwargs['k3s'] = kwargs['ksl'][3]
        except: KeyError
    try: kwargs['knl'] = list(kwargs['knl'])
    except: KeyError
    try: kwargs['ksl'] = list(kwargs['ksl'])
    except: KeyError
    madx.command[element_type].clone(element.name, **kwargs)
    return madx


def from_pyat(el_class, element): 
    """ 
    Create specific Element instance from pyAT element
    
    Args:
        el_class: framework specific Element class 
            i.e. Quadrupole, RFCavity, ...
        element: pyAT Element instance
    """
    attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 
                'NumIntSteps':'NumIntSteps', 'knl':'PolynomB', 'ksl':'PolynomA',
                'angle':'BendingAngle', 'e1':'EntranceAngle', 'e2':'ExitAngle', 
                'volt':'Voltage', 'freq':'Frequency', 'energy':'Energy'}
    kwargs = {}
    for key in attr_dict.keys():
        try: kwargs[key] = getattr(element, attr_dict[key])
        except: AttributeError
    return el_class(element.FamName, **kwargs)


def to_pyat(element):
    """ 
    Create pyAT Element instance from element

    Args:
        element: fff Element instance
    """
    attr_dict = {'PassMethod':'PassMethod', 'harmonic_number':'harmonic_number',
                'NumIntSteps':'NumIntSteps', 'PolynomB':'knl', 'PolynomA':'ksl',
                'BendingAngle':'angle', 'EntranceAngle':'e1', 'ExitAngle':'e2', 
                'Voltage':'volt', 'Frequency':'freq', 'Energy':'energy'}

    aper_kwarg = {}
    try:
        if element.aperture[0] == 0 or element.aperture[1] == 0:
            aper_kwarg = {}
        else: 
            if element.apertype == 'circle':
                aper_kwarg = {'EApertures':[element.aperture[0], element.aperture[0]]}
            elif element.apertype == 'ellipse':
                aper_kwarg = {'EApertures':[element.aperture[0], element.aperture[1]]}
            elif element.apertype == 'rectangle':
                aper_kwarg = {'RApertures':[-element.aperture[0], element.aperture[0], 
                                            -element.aperture[1], element.aperture[1]]}
    except AttributeError:
        pass

    kwargs = {}
    for key in attr_dict.keys():
        try: kwargs[key] = getattr(element, attr_dict[key])
        except: AttributeError
    kwargs.update(aper_kwarg)
    
    if element.__class__.__name__ == 'Marker':
        return lel.FFF_TO_PYAT_MAP[element.__class__.__name__](element.name, **kwargs)
    elif element.__class__.__name__ == 'RFCavity':
        return lel.FFF_TO_PYAT_MAP[element.__class__.__name__](element.name, element.length, element.volt, 
                                                            element.freq, element.harmonic_number, 
                                                            element.energy)
    else:
        return lel.FFF_TO_PYAT_MAP[element.__class__.__name__](element.name, element.length, **kwargs)