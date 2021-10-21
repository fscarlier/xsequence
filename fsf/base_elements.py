import math
from abc import ABC, abstractmethod
from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np


@dataclass
class ElementID:
    INIT_PROPERTIES = ['slot_id', 'assembly']
    slot_id: Optional[int] = None
    assembly: Optional[int] = None


@dataclass
class ElementPosition:
    INIT_PROPERTIES = ['length', 'distance', 'reference', 'tilt', 'mech_sep']
    length: float = 0.0
    _length: float = field(init=False, repr=False, default=0.0)
    distance: float = 0.0
    _distance: float = field(init=False, repr=False, default=0.0)
    reference: float = 0.0
    _reference: float = field(init=False, repr=False, default=0.0)
    tilt: float = 0.0
    mech_sep: float = 0.0

    def __post_init__(self):
        if isinstance(self.length, property):
            self.length = 0.0
        if isinstance(self.distance, property):
            self.distance = 0.0
        if isinstance(self.reference, property):
            self.reference = 0.0
    
    @property
    def length(self) -> float:
        return self._length

    @length.setter
    def length(self, length: float):
        self._length = length
        self.calc_position()

    @property
    def distance(self) -> float:
        return self._distance

    @distance.setter
    def distance(self, distance: float):
        self._distance = distance
        self.calc_position()

    @property
    def reference(self) -> float:
        return self._reference

    @reference.setter
    def reference(self, reference: float):
        self._reference = reference
        self.calc_position()
    
    @property
    def position(self) -> float:
        return self.get_position(loc='centre')

    def get_position(self, loc='centre'):
        assert loc in ['centre', 'start', 'end']
        if self._position == None: 
            self.calc_position()
        return self._position[loc]

    def set_position(self, distance=0, reference=0):
        self._reference = reference
        self._distance = distance
        self.calc_position()

    def calc_position(self):
        try:
            pos = self.distance + self.reference
            self._position = {'centre':pos, 
                            'start':pos - self.length/2.,
                            'end':pos + self.length/2.}
        except: AttributeError


@dataclass
class Aperture:
    """Represents an aperture for elements"""
    pass


@dataclass
class CircularAperture(Aperture):
    INIT_PROPERTIES = ['aperture_size', 'aperture_type', 'aperture_offset']
    aperture_size: List
    aperture_type: Optional[str] = 'circular'
    aperture_offset: Optional[float] = 0.0


@dataclass
class BendData:
    """ Bend strength dataclass """
    INIT_PROPERTIES = ['angle', 'e1', 'e2', 'k0']
    angle: float = 0.0
    e1: float = 0.0
    e2: float = 0.0
    k0: Optional[float] = 0.0  


@dataclass
class SolenoidData:
    """ Solenoid strength dataclass """
    INIT_PROPERTIES = ['ks']
    ks: float = 0.0
    ksi: float = None


@dataclass
class DipoleEdgeData:
    """ Dipole edge strength dataclass """
    INIT_PROPERTIES = ['h', 'e1', 'side']
    h: float 
    e1: float 
    side: str 
    
    def __post_init__(self):
        assert self.side in ('entrance', 'exit'), f"Invalid side Attribute for DipoleEdgeData"


@dataclass
class MultipoleStrengthData:
    INIT_PROPERTIES = ['kn', 'ks', 'polarity']
    kn: List = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])  
    ks: List = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0]) 
    polarity: int = None  

    def __post_init__(self):
        self._update_arrays()

    def _update_arrays(self, min_order=1):
        kn = np.trim_zeros(self.kn, trim='b')
        ks = np.trim_zeros(self.ks, trim='b')
        if len(kn) == 0: kn = np.zeros(1)
        if len(ks) == 0: ks = np.zeros(1)
        self.order = max(len(kn), len(ks), min_order)
        self.kn = np.pad(kn, (0, self.order-len(kn)))
        self.ks = np.pad(ks, (0, self.order-len(ks)))


@dataclass
class ThinMultipoleStrengthData:
    INIT_PROPERTIES = ['knl', 'ksl', 'polarity']
    knl: List = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])  
    ksl: List = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0]) 
    polarity: int = None  

    def __post_init__(self):
        self._update_arrays()

    def _update_arrays(self, min_order=1):
        knl = np.trim_zeros(self.knl, trim='b')
        ksl = np.trim_zeros(self.ksl, trim='b')
        if len(knl) == 0: knl = np.zeros(1)
        if len(ksl) == 0: ksl = np.zeros(1)
        self.order = max(len(knl), len(ksl), min_order)
        self.knl = np.pad(knl, (0, self.order-len(knl)))
        self.ksl = np.pad(ksl, (0, self.order-len(ksl)))


@dataclass
class QuadrupoleData(MultipoleStrengthData):
    INIT_PROPERTIES = ['k1', 'k1s', 'kmax', 'kmin']
    k1: float = 0.0
    k1s: float = 0.0
    kmax: float = None
    kmin: float = None
    
    def __post_init__(self):
        if isinstance(self.k1, property):
            self.k1 = 0.0
        self._update_arrays(min_order=2)
    
    @property
    def k1(self):
        return self.kn[1]

    @k1.setter
    def k1(self, k1: float):
        self.kn[1] = k1


@dataclass
class SextupoleData(MultipoleStrengthData):
    INIT_PROPERTIES = ['k2', 'k2s', 'kmax', 'kmin']
    k2: float = 0.0
    k2s: float = 0.0
    kmax: float = None
    kmin: float = None

    def __post_init__(self):
        if isinstance(self.k2, property):
            self.k2 = 0.0
        self._update_arrays(min_order=3)

    @property
    def k2(self):
        return self.kn[2]

    @k2.setter
    def k2(self, k2: float):
        self.kn[2] = k2


@dataclass
class OctupoleData(MultipoleStrengthData):
    INIT_PROPERTIES = ['k3', 'k3s', 'kmax', 'kmin']
    k3: float = 0.0
    k3s: float = 0.0
    kmax: float = None
    kmin: float = None

    def __post_init__(self):
        if isinstance(self.k3, property):
            self.k3 = 0.0
        self._update_arrays(min_order=4)

    @property
    def k3(self):
        return self.kn[3]

    @k3.setter
    def k3(self, k3: float):
        self.kn[3] = k3


@dataclass
class RFCavityData():
    INIT_PROPERTIES = ['voltage', 'frequency', 'lag']
    voltage: float = 0.0  
    frequency: float = 0.0 
    lag: float = 0.0 


@dataclass
class HKickerData():
    hkick: float  


@dataclass
class VKickerData():
    vkick: float  


@dataclass
class KickerData():
    kick: float  


class BaseElement():
    """Class containing base element properties and methods"""
    def __init__(self, name, bend_class=None, strength_class=None, rf_class=None, **kwargs):
        self.name = name
        if kwargs is not None:
            kwargs = {'temp':0}
        self.element_id = ElementID(**{k:kwargs[k] for k in ElementID.INIT_PROPERTIES if k in kwargs})
        self.position = ElementPosition(**{k:kwargs[k] for k in ElementPosition.INIT_PROPERTIES if k in kwargs})
        self.aperture = Aperture()
        if bend_class:
            self.bend = bend_class(**{k:kwargs[k] for k in bend_class.INIT_PROPERTIES if k in kwargs})
        if strength_class:
            self.strength = strength_class(**{k:kwargs[k] for k in strength_class.INIT_PROPERTIES if k in kwargs})
        if rf_class:
            self.rf_params = rf_class(**{k:kwargs[k] for k in rf_class.INIT_PROPERTIES if k in kwargs})

    @property
    def length(self):
        return self.position.length
    
    @length.setter
    def length(self, length):
        self.position.length = length

    def _get_repr(self) -> str:
        return f'{self.name}, element_id={self.element_id}, position={self.position}, aperture={self.aperture}' 

    def __repr__(self) -> str:
        return f'{self.name}, element_id={self.element_id}, position={self.position}, aperture={self.aperture}' 


class Marker(BaseElement):
    """ Marker element class """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length == 0.0, f"Marker {name} has non-zero length"
    

class Drift(BaseElement):
    """ Drift element class """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length > 0.0, f"Drift {name} has zero or negative length"


class Collimator(Drift):
    """ Collimator element class """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Monitor(Drift):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Placeholder(Drift):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Instrument(Drift):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class SectorBend(BaseElement):
    """ Sbend element class """
    def __init__(self, name, bend_class=BendData, **kwargs):
        super().__init__(name, bend_class=bend_class, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + super().__repr__() + f', bend={self.bend})'

    def _calc_length(self, angle, chord_length):
        return (angle*chord_length)/(2*math.sin(angle/2.))

    def _calc_chordlength(self, angle, length) :
        return length*(2*math.sin(angle/2.))/angle


class Rectangularbend(BaseElement):   
    """ Rbend element class """
    def __init__(self, name, bend_class=BendData, **kwargs):
        self._chord_length = kwargs.pop('length', 0)
        self._rbend_e1 = kwargs.pop('e1', 0)
        self._rbend_e2 = kwargs.pop('e2', 0)
        kwargs['length'] = self._calc_length(kwargs['angle'], self._chord_length)
        kwargs['e1'] = self._rbend_e1+abs(kwargs['angle'])/2.
        kwargs['e2'] = self._rbend_e2+abs(kwargs['angle'])/2.
        
        super().__init__(name, bend_class=bend_class, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + super().__repr__() + f', bend={self.bend})'


class DipoleEdge(BaseElement):
    """ Dipole edge element class """
    def __init__(self, name, strength_class=DipoleEdgeData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + super().__repr__() + f', strength={self.strength})'


class Solenoid(BaseElement):
    """ Solenoid element class """
    def __init__(self, name, strength_class=SolenoidData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + super().__repr__() + f', strength={self.strength})'
         
    @property
    def ks(self):
        return self.strength.ks
    
    @ks.setter
    def ks(self, ks):
        self.strength.ks = ks

    @property
    def ksi(self):
        return self.strength.ks*self.length
    
    @ks.setter
    def ks(self, ksi):
        self.strength.ks = ksi/self.length


class Multipole(BaseElement):
    """ Multipole element class """
    def __init__(self, name, strength_class=MultipoleStrengthData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + super().__repr__() + f', strength={self.strength})'

    @property
    def knl(self):
        return self.strength.kn*self.length
    
    @knl.setter
    def knl(self, knl):
        self.strength.kn = knl/self.length


class Quadrupole(Multipole):
    """ Quadrupole element class """
    def __init__(self, name, strength_class=QuadrupoleData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)

    @property
    def k1(self):
        return self.strength.k1
    
    @k1.setter
    def k1(self, k1):
        self.strength.k1 = k1

    @property
    def k1s(self):
        return self.strength.k1s
    
    @k1s.setter
    def k1s(self, k1s):
        self.strength.k1s = k1s


class Sextupole(Multipole):
    """ Sextupole element class """
    def __init__(self, name, strength_class=SextupoleData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)

    @property
    def k2(self):
        return self.strength.k2
    
    @k2.setter
    def k1(self, k2):
        self.strength.k2 = k2

    @property
    def k2s(self):
        return self.strength.k2s
    
    @k2s.setter
    def k2s(self, k2s):
        self.strength.k2s = k2s


class Octupole(Multipole):
    """ Octupole element class """
    def __init__(self, name, strength_class=OctupoleData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)

    @property
    def k3(self):
        return self.strength.k3
    
    @k3.setter
    def k3(self, k3):
        self.strength.k3 = k3

    @property
    def k3s(self):
        return self.strength.k3s
    
    @k3s.setter
    def k3s(self, k3s):
        self.strength.k3s = k3s


class RFCavity(BaseElement):
    """ RFCavity element class """
    def __init__(self, name, rf_class=RFCavityData, **kwargs):
        super().__init__(name, rf_class=rf_class, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}(' + super().__repr__() + f', rf_params={self.rf_params})'
    

class HKicker(BaseElement):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class VKicker(BaseElement):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TKicker(BaseElement):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinMultipole(BaseElement):
    """ Thin multipole element class """
    def __init__(self, name, strength_class=ThinMultipoleStrengthData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)
        self.length_radiation = kwargs.pop('length_radiation', 0)
        assert self.length == 0


class ThinSolenoid(Solenoid):
    """ ThinSolenoid element class """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.length_radiation = kwargs.pop('length_radiation', 0)
        assert self.length == 0

class ThinRFMultipole(RFCavity):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.length_radiation = kwargs.pop('length_radiation', 0)
        assert self.length == 0

