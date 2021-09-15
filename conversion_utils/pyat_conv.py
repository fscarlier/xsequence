import at


def get_aperture_kwarg(element):
    aper_kwarg = {}
    try:
        if len(element.aperture) == 1 and element.aperture[0] == 0: 
            aper_kwarg = {}
        elif len(element.aperture) == 2:
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
    return aper_kwarg


def get_element_kwargs(element, attr_dict):
    aper_kwarg = get_aperture_kwarg(element)
    kwargs = {}
    for key in attr_dict.keys():
        try: kwargs[key] = getattr(element, attr_dict[key])
        except: AttributeError
    kwargs.update(aper_kwarg)
    return kwargs


def to_pyat_marker(element):
    return at.elements.Marker(element.name)
    

def to_pyat_drift(element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'NumIntSteps', }
    kwargs = get_element_kwargs(element, attr_dict)
    return at.elements.Drift(element.name, element.length, **kwargs)
    

def to_pyat_sbend(element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'NumIntSteps', 'PolynomB':'knl', 
                 'PolynomA':'ksl', 'BendingAngle':'angle', 'EntranceAngle':'e1', 'ExitAngle':'e2'}
    kwargs = get_element_kwargs(element, attr_dict)
    return at.elements.Dipole(element.name, element.length, **kwargs)
 
 
def to_pyat_rbend(element):
    sbend = element.convert_to_sbend()
    return to_pyat_sbend(sbend)


def to_pyat_quadrupole(element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'NumIntSteps', 'PolynomB':'knl', 'PolynomA':'ksl'}
    kwargs = get_element_kwargs(element, attr_dict)
    return at.elements.Dipole(element.name, element.length, **kwargs)



def to_pyat_sextupole(element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'NumIntSteps', 'PolynomB':'knl', 'PolynomA':'ksl'}
    kwargs = get_element_kwargs(element, attr_dict)
    return at.elements.Dipole(element.name, element.length, **kwargs)


def to_pyat_octupole(element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'NumIntSteps', 'PolynomB':'knl', 'PolynomA':'ksl'}
    kwargs = get_element_kwargs(element, attr_dict)
    return at.elements.Dipole(element.name, element.length, **kwargs)


def to_pyat_collimator(element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'NumIntSteps', }
    kwargs = get_element_kwargs(element, attr_dict)
    return at.elements.Dipole(element.name, element.length, **kwargs)


def to_pyat_rfcavity(element):
    attr_dict = {'PassMethod':'PassMethod', 'NumIntSteps':'NumIntSteps', 'PolynomB':'knl', 'PolynomA':'ksl'}
    kwargs = get_element_kwargs(element, attr_dict)
    return at.elements.RFCavity(element.name, element.length, element.volt*1e6, element.freq*1e6, 
                                element.harmonic_number, element.energy*1e9, **kwargs)


def convert_element(element):
    return CONVERSIONS[element.__class__.__name__](element)


CONVERSIONS = {'Marker': to_pyat_marker, 
               'Drift':  to_pyat_drift, 
               'Sbend':  to_pyat_sbend, 
               'Rbend':  to_pyat_rbend, 
               'Quadrupole': to_pyat_quadrupole, 
               'Sextupole': to_pyat_sextupole, 
               'Collimator': to_pyat_collimator, 
               'RFCavity': to_pyat_rfcavity}