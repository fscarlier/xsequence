import os, sys
import copy
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
        self.parent = kwargs.pop('parent', self.__class__.__name__)
        self.update(**kwargs)

    def __eq__(self, other):
        return self.__dict__ == other.__dict__

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

    @property
    def pos(self):
        return self._position 

    @pos.setter
    def pos(self, position):
        self._position = position


class Drift(Element):
    """
    Drift element class

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
        super().__init__(name, **kwargs)
        assert self.length >= 0.0, f"Drift {name} has negative length"


class Marker(Element):
    """
    Marker element class
    
    Attributes
    ----------
    name : string
        name of element
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length == 0.0, f"Marker {name} has non-zero length"


class Sbend(Element):   
    """
    Dipole element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
        arc length of bending magnet
    chord_length : float
        straight line length from entry to exit (see rbends in MAD-X)
    angle : float
        bending angle of bend magnet
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from 'angle' and 'chord_length' 

    _calc_chordlength()
        Calculate chordlength from 'angle' and 'length' ('arc_length')

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.chord_length = kwargs.pop('chord_length', self._calc_chordlength())
        assert np.isclose(self.length, self._calc_arclength(), rtol=1e-8), f"{self.length},  {self._calc_arclength()}"
    
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.length*(2*np.sin(self.angle/2.))/self.angle

    def convert_to_rbend(self):
        kwargs = copy.copy(vars(self))
        kwargs['arc_length'] = kwargs.pop('length')
        kwargs['length'] = kwargs.pop('chord_length')
        if 'e1' in kwargs:
            kwargs['e1'] = kwargs.pop('e1')-self.angle/2.
        if 'e2' in kwargs:
            kwargs['e2'] = kwargs.pop('e2')-self.angle/2.
        kwargs.pop('name')
        return Rbend(self.name, **kwargs) 


class Rbend(Element):   
    """
    Dipole element class
    
    Attributes
    ----------
    name : string
        name of element
    length : float
         chord length of bending magnet from entry to exit (see rbends in MAD-X)
    arc_length : float
        arc length of bending magnet
    angle : float
        bending angle of bend magnet
    
    Methods
    -------
    _calc_arclength()
        Calculate arclength from 'angle' and 'length' ('chord_length')

    _calc_chordlength()
        Calculate chordlength from 'angle' and 'arc_length' 

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.arc_length = kwargs.pop('arc_length', self._calc_arclength())
        assert np.isclose(self.length, self._calc_chordlength(), rtol=1e-8)
     
    def _calc_arclength(self) :
        """ Calculate arc length from angle and chord length """
        return (self.angle*self.length)/(2*np.sin(self.angle/2.))

    def _calc_chordlength(self) :
        """ Calculate chord length from angle and arc length """
        return self.arc_length*(2*np.sin(self.angle/2.))/self.angle

    def convert_to_sbend(self):
        kwargs = copy.copy(vars(self))
        kwargs['chord_length'] = kwargs.pop('length')
        kwargs['length'] = kwargs.pop('arc_length')
        if 'e1' in kwargs:
            kwargs['e1'] = kwargs.pop('e1')+self.angle/2.
        if 'e2' in kwargs:
            kwargs['e2'] = kwargs.pop('e2')+self.angle/2.
        kwargs.pop('name')
        return Sbend(self.name, **kwargs) 


class Quadrupole(Element):
    """
    Quadrupole element class
    
    Attributes
    ----------
    name : string
        name of element
    knl : float array
        normal magnetic strengths array to arbitrary order
    ksl : float array
        skew magnetic strengths array to arbitrary order

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Sextupole(Element):
    """
    Sextupole element class
    
    Attributes
    ----------
    name : string
        name of element
    knl : float array
        normal magnetic strengths array to arbitrary order
    ksl : float array
        skew magnetic strengths array to arbitrary order

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Octupole(Element):
    """
    Octupole element class
    
    Attributes
    ----------
    name : string
        name of element
    knl : float array
        normal magnetic strengths array to arbitrary order
    ksl : float array
        skew magnetic strengths array to arbitrary order

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class RFCavity(Element):
    """
    RFCavity element class
    
    Attributes
    ----------
    name : string
        name of element
    volt : float
        peak electrical rf voltage
    freq : float
        frequency of rfcavity in MHz
    harmon : integer
        harmonic number h 

    """
    def __init__(self, name, **kwargs):
        self.volt = kwargs.pop('volt', 0.0)
        self.freq = kwargs.pop('freq', 0.0)
        super().__init__(name, **kwargs)


class Collimator(Drift):
    """
    Collimator element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Solenoid(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinMultipole(Element):
    """
    Solenoid element class
    
    Attributes
    ----------
    order : int
        Multipolar order of element

    """
    def __init__(self, name, order=1, **kwargs):
        self.knl = kwargs.pop('knl', np.zeros(order))
        self.ksl = kwargs.pop('ksl', np.zeros(order)) 
        super().__init__(name, **kwargs)

    
class BeamBeam(Element):
    """
    Beam-beam element class
    
    Attributes
    ----------
    charge : int
        charge of particles in the opposite beam
    sigx : float
        horizontal beam size of opposite beam
    sigy : float
        vertical beam size of opposite beam
    dx : float
        horizontal orbit offset of opposite beam
    dy : float
        vertical orbit offset of opposite beam
    shape : str
        radial density shape of the opposite beam, default='gaussian'
    """
    def __init__(self, name, **kwargs):
        self.charge = kwargs.pop('charge', 1)
        self.sigx = kwargs.pop('sigx', 1)
        self.sigy = kwargs.pop('sigy', 1)
        self.dx = kwargs.pop('dx', 0)
        self.dy = kwargs.pop('dy', 0)
        self.shape = kwargs.pop('shape', 'gaussian')
        super().__init__(name, **kwargs)


class DipoleEdge(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ClosedOrbitCorrector(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TransverseKicker(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TravellingWaveCavity(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinRFMultipole(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class CrabCavity(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ACDipole(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ElectrostaticSeparator(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamPositionMonitor(Element):
    """
    Solenoid element class
    
    Attributes
    ----------

    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Instrument(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Placeholder(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ArbitraryMatrixElement(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


