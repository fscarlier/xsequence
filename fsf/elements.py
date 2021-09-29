import copy
import at
import numpy as np
from conversion_utils import pyat_conv, cpymad_conv


class Element:
    """
    Base element class  
    """

    def __init__(self, name, **kwargs):
        """
        Args:
            name : string
                name of element
        
        Key Args:
            length: float
                length of element [m]
        """
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
    def position(self):
        return self.pos 


    @position.setter
    def position(self, position):
        self.pos = position


    @classmethod
    def from_cpymad(cls, cpymad_element):
        """ 
        Create specific Element instance from cpymad element
        """
        return cpymad_conv.convert_element_from_cpymad(cls, cpymad_element)


    def to_cpymad(self, madx):
        """ 
        Create cpymad element in madx instance from Element
        """
        return cpymad_conv.convert_element_to_cpymad(self, madx)


    @classmethod
    def from_pyat(cls, pyat_element):
        """ 
        Create specific Element instance from pyAT element
        """
        return pyat_conv.convert_element_from_pyat(cls, pyat_element)


    def to_pyat(self):
        """ 
        Create pyAT Element instance from element
        """
        return pyat_conv.convert_element_to_pyat(self)


    @property
    def int_steps(self):
        return self._int_steps 


    @int_steps.setter
    def int_steps(self, int_steps):
        self._int_steps = int_steps 


class Drift(Element):
    """
    Drift element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length >= 0.0, f"Drift {name} has negative length"


class Marker(Element):
    """
    Marker element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length == 0.0, f"Marker {name} has non-zero length"


class Sbend(Element):   
    """
    Sbend element class
    """
    def __init__(self, name, **kwargs):
        """
        Args:
            name : string
                name of element
        
        Key Args:
            length: float
                arclength of element [m]
        """
        super().__init__(name, **kwargs)
        self.chord_length = kwargs.pop('chord_length', self._calc_chordlength())

    
    def _calc_arclength(self) :
        """
        Calculate arclength from angle and chordlength
        
        Returns:
            Float with arclength
        """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))


    def _calc_chordlength(self) :
        """
        Calculate chordlength from angle and arclength
        
        Returns:
            Float with chordlength 
        """
        return self.length*(2*np.sin(self.angle/2.))/self.angle


    def convert_to_rbend(self):
        """
        Convert Sbend element to Rbend element
        
        Returns:
            Rbend instance of element 
        """
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
    Rbend element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.arc_length = kwargs.pop('arc_length', self._calc_arclength())
        assert np.isclose(self.length, self._calc_chordlength(), rtol=1e-8)

     
    def _calc_arclength(self) :
        """
        Calculate arclength from angle and chordlength
        
        Returns:
            Float with arclength
        """
        return (self.angle*self.length)/(2*np.sin(self.angle/2.))


    def _calc_chordlength(self) :
        """
        Calculate chordlength from angle and arclength
        
        Returns:
            Float with chordlength 
        """
        return self.arc_length*(2*np.sin(self.angle/2.))/self.angle


    def convert_to_sbend(self):
        """
        Convert Rbend element to Sbend element
        
        Returns:
            Sbend instance of element 
        """
        kwargs = copy.copy(vars(self))
        kwargs['chord_length'] = kwargs.pop('length')
        kwargs['length'] = kwargs.pop('arc_length')
        if 'e1' in kwargs:
            kwargs['e1'] = kwargs.pop('e1')+abs(self.angle)/2.
        if 'e2' in kwargs:
            kwargs['e2'] = kwargs.pop('e2')+abs(self.angle)/2.
        kwargs.pop('name')
        return Sbend(self.name, **kwargs) 


class Multipole(Element):
    """
    Multipole element class
    """
    def __init__(self, name, **kwargs):
        """
        Setting multipole strengths. knl and ksl have precedence over k1, k2, k3
        """
        self.length = kwargs['length']
        assert self.length != 0, "Thick {} ({}) defined with length 0. Use Thin{} instead"\
                                 .format(self.__class__.__name__, name, self.__class__.__name__)
        self.kn = np.array(kwargs.pop('kn', [kwargs.pop('k0', 0.0), kwargs.pop('k1', 0.0), 
                                             kwargs.pop('k2', 0.0), kwargs.pop('k3', 0.0)]))
        self.ks = np.array(kwargs.pop('ks', [kwargs.pop('k0s', 0.0), kwargs.pop('k1s', 0.0), 
                                             kwargs.pop('k2s', 0.0), kwargs.pop('k3s', 0.0)]))
        self.knl = np.array(kwargs.pop('knl', self.kn*self.length)) 
        self.ksl = np.array(kwargs.pop('ksl', self.ks*self.length))
        self.order = max(len(self.knl), len(self.ksl))
        super().__init__(name, **kwargs)


class Quadrupole(Multipole):
    """
    Quadrupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    @property
    def k1(self):
        return self.kn[1]
    
    @k1.setter
    def k1(self, k):
        self.kn[1] = k

    @property
    def k1s(self):
        return self.ks[1]
    
    @k1s.setter
    def k1s(self, ks):
        self.ks[1] = ks


class Sextupole(Multipole):
    """
    Sextupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    @property
    def k2(self):
        return self.kn[2]
    
    @k2.setter
    def k2(self, k):
        self.kn[2] = k

    @property
    def k2s(self):
        return self.ks[2]
    
    @k2s.setter
    def k2s(self, ks):
        self.ks[2] = ks


class Octupole(Multipole):
    """
    Octupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    @property
    def k3(self):
        return self.kn[3]
    
    @k3.setter
    def k3(self, k):
        self.kn[3] = k

    @property
    def k3s(self):
        return self.ks[3]
    
    @k3s.setter
    def k3s(self, ks):
        self.ks[3] = ks


class ThinMultipole(Element):
    """
    Multipole element class
    """
    def __init__(self, name, **kwargs):
        self.knl = np.array(kwargs.pop('knl'))
        self.ksl = np.array(kwargs.pop('ksl'))
        super().__init__(name, **kwargs)
        assert self.length == 0, "Thin{} ({}) defined with length > 0. Use {} instead"\
                                 .format(self.__class__.__name__, name, self.__class__.__name__)


class ThinQuadrupole(ThinMultipole):
    """
    Thin Quadrupole class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinSextupole(ThinMultipole):
    """
    Thin Sextupole class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinOctupole(ThinMultipole):
    """
    Thin Octupole class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class RFCavity(Element):
    """
    RFCavity element class
    """
    def __init__(self, name, **kwargs):
        self.volt = kwargs.pop('volt', 0.0)
        self.freq = kwargs.pop('freq', 0.0)
        super().__init__(name, **kwargs)


class Collimator(Drift):
    """
    Collimator element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Solenoid(Element):
    """
    Solenoid element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    
class BeamBeam(Element):
    """
    Beam-beam element class
    
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
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ClosedOrbitCorrector(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TransverseKicker(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TravellingWaveCavity(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinRFMultipole(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class CrabCavity(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ACDipole(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ElectrostaticSeparator(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamPositionMonitor(Element):
    """
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

