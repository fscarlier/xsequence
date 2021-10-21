"""
Module fsf.base_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element dataclasses for particle accelerator elements.
"""

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

    def get_position(self, loc: str ='centre'):
        assert loc in ['centre', 'start', 'end']
        if self._position == None: 
            self.calc_position()
        return self._position[loc]

    def set_position(self, distance: float = 0.0, reference: float = 0.0):
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

    def _update_arrays(self, min_order: int = 1):
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

    def _update_arrays(self, min_order: int = 1):
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
