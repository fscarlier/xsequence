import numpy as np


class Element:
    """
    Base element class  

    Attributes
    ----------
    name : string
        name of element
    length : float
        length of element

    Methods
    -------
    update  
        update element attributes from **kwargs

    """

    def __init__(self, name, **kwargs):
        self.name = name
        self.length = kwargs.pop('length', 0.0)
        self.update(**kwargs)

    def __str__(self):
        args_dict = vars(self).items()
        args_str = [f'{k}={v}' for k,v in args_dict if k!= 'name']
        return f"{self.__class__.__name__}('{self.name}', {', '.join(args_str)})"

    def __repr__(self):
        args_dict = vars(self).items()
        args_str = [f'{k}={v}' for k,v in args_dict if k!= 'name']
        return f"{self.__class__.__name__}('{self.name}', {', '.join(args_str)})"

    def update(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def items(self):
        """Iterates through the data members including slots and properties"""
        # Get attributes
        for k, v in vars(self).items():
            yield k, v
        # Get slots and properties
        for k, v in getmembers(self.__class__, isdatadescriptor):
            if not k.startswith('_'):
                yield k, getattr(self, k)


class Drift(Element):
    """
    Drift specifc element class

    Attributes
    ----------
    name : string
        name of element
    length : float
        length of element, cannot be 0.0

    Methods
    -------
    string
        a value in a string

    """
    def __init__(self, name, **kwargs):
        # assert kwargs['length'] > 0.0
        super().__init__(name, **kwargs)


class Marker(Element):
    """
    Marker specifc element class
    
    Attributes
    ----------
    name : string
        name of element
    """
    def __init__(self, name, **kwargs):
        assert kwargs['length'] == 0.0
        super().__init__(name, **kwargs)


class Dipole(Element):   
    """
    Dipole specific element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
        arc_length of bending magnet
    chord_length : float
        straight line length from entry to exit (see rbends in MAD-X)
    angle : float
        bending angle of bend magnet
    bend_type : string
        'sbend' or 'rbend', see MAD-X documentation
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, angle=0.0, bend_type='sbend', **kwargs):
        self.bend_type = kwargs.pop('bend_type')
        self.angle = kwargs.pop('angle')

        if self.bend_type == 'sbend':
            self.length = kwargs.pop('length', 0.0)
            self.chord_length = self._calc_chordlength() 
        elif self.bend_type == 'rbend':
            self.chord_length = kwargs.pop('chord_length', 0.0)
            self.length = self._calc_arclength() 
        self.e1 = kwargs.pop('e1', 0.0)
        self.e2 = kwargs.pop('e2', 0.0)
        super().__init__(name, **kwargs)
     
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.length*(2*np.sin(self.angle/2.))/self.angle


class Sbend(Element):   
    """
    Dipole specific element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
        arc_length of bending magnet
    chord_length : float
        straight line length from entry to exit (see rbends in MAD-X)
    angle : float
        bending angle of bend magnet
    bend_type : string
        'sbend' or 'rbend', see MAD-X documentation
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.chord_length = self._calc_chordlength() 
    
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.length*(2*np.sin(self.angle/2.))/self.angle


class Rbend(Element):   
    """
    Dipole specific element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
        arc_length of bending magnet
    chord_length : float
        straight line length from entry to exit (see rbends in MAD-X)
    angle : float
        bending angle of bend magnet
    bend_type : string
        'sbend' or 'rbend', see MAD-X documentation
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.arc_length = self._calc_arclength() 
     
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.arc_length*(2*np.sin(self.angle/2.))/self.angle


class Quadrupole(Element):
    """
    Quadrupole specifc element class
    
    Attributes
    ----------
    name : string
        name of element
    knl : float array
        normal magnetic strengths array to arbitrary order
    ksl : float array
        skew magnetic strengths array to arbitrary order
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from angle and rbend r_length

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.knl = kwargs.pop('knl', [0.0, 0.0])
        self.ksl = kwargs.pop('ksl', [0.0, 0.0])


class Sextupole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.knl = kwargs.pop('knl', [0.0, 0.0, 0.0])
        self.ksl = kwargs.pop('ksl', [0.0, 0.0, 0.0])


class Octupole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class RFCavity(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.volt = kwargs.pop('volt', 0.0)
        self.freq = kwargs.pop('freq', 0.0)

class Solenoid(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinMultipole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    
class DipoleEdge(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ClosedOrbitCorrector(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TransverseKicker(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TravellingWaveCavity(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinRFMultipole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class CrabCavity(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ACDipole(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ElectrostaticSeparator(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamPositionMonitor(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Instrument(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Placeholder(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Collimator(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamBeam(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ArbitraryMatrixElement(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)




