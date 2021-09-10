import copy
import numpy as np


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
    def from_cpymad(cls, element):
        name = element.name.replace('.', '_').lower()
        base_type = element.base_type.name

        if name == base_type:
            kwargs = dict(element.items())
            kwargs['position'] = kwargs.pop('at')
            kwargs['length'] = kwargs.pop('l')
            return cls(name, **kwargs)
        
        kwargs_element = {k: v.value for k, v in element._data.items() if v.inform}
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
        return cls(name, **kwargs)


    @classmethod
    def from_pyat(cls, el):
        attr_dict = {'length':'Length', 'PassMethod':'PassMethod', 
                    'NumIntSteps':'NumIntSteps', 'knl':'PolynomB', 'ksl':'PolynomA',
                    'angle':'BendingAngle', 'e1':'EntranceAngle', 'e2':'ExitAngle', 
                    'volt':'Voltage', 'freq':'Frequency', 'energy':'Energy'}
        kwargs = {}
        for key in attr_dict.keys():
            try: kwargs[key] = getattr(el, attr_dict[key])
            except: AttributeError
        return cls(el.FamName, **kwargs)



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
        assert np.isclose(self.length, self._calc_arclength(), rtol=1e-8), f"{self.length},  {self._calc_arclength()}"

    
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
            kwargs['e1'] = kwargs.pop('e1')+self.angle/2.
        if 'e2' in kwargs:
            kwargs['e2'] = kwargs.pop('e2')+self.angle/2.
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
        self.knl = np.array(kwargs.pop('knl', [kwargs.pop('k0', 0.0), 
                                               kwargs.pop('k1', 0.0), 
                                               kwargs.pop('k2', 0.0), 
                                               kwargs.pop('k3', 0.0)]))
        self.ksl = np.array(kwargs.pop('ksl', [kwargs.pop('k0s', 0.0), 
                                               kwargs.pop('k1s', 0.0), 
                                               kwargs.pop('k2s', 0.0), 
                                               kwargs.pop('k3s', 0.0)]))
        super().__init__(name, **kwargs)


class Quadrupole(Multipole):
    """
    Quadrupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Sextupole(Multipole):
    """
    Sextupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Octupole(Multipole):
    """
    Octupole element class
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


