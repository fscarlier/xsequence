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
    """ Dataclass containing all relevant information about element position in [m] """
    INIT_PROPERTIES = ['length', 'location', 'reference', 'tilt', 'mech_sep']
    length: float = 0.0
    _length: float = field(init=False, repr=False, default=0.0)
    location: float = 0.0
    _location: float = field(init=False, repr=False, default=0.0)
    reference: float = 0.0
    _reference: float = field(init=False, repr=False, default=0.0)
    tilt: float = 0.0
    mech_sep: float = 0.0

    def __post_init__(self):
        if isinstance(self.length, property):
            self.length = 0.0
        if isinstance(self.location, property):
            self.location = 0.0
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
    def location(self) -> float:
        return self._location

    @location.setter
    def location(self, location: float):
        self._location = location
        self.calc_position()

    @property
    def reference(self) -> float:
        return self._reference

    @reference.setter
    def reference(self, reference: float):
        self._reference = reference
        self.calc_position()
    
    @property
    def start(self) -> float:
        return self.get_position(loc='start')
    
    @property
    def position(self) -> float:
        return self.get_position(loc='centre')
    
    @property
    def end(self) -> float:
        return self.get_position(loc='end')

    def get_position(self, loc: str ='centre'):
        assert loc in ['centre', 'start', 'end']
        if self._position == None: 
            self.calc_position()
        return self._position[loc]

    def set_position(self, location: float = 0.0, reference: float = 0.0):
        self._reference = reference
        self._location = location
        self.calc_position()

    def calc_position(self):
        try:
            pos = self.location + self.reference
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
    aperture_size: float = 0.0
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


@dataclass
class ThinSolenoidData:
    """ Solenoid strength dataclass """
    INIT_PROPERTIES = ['ksi']
    ksi: float = 0.0


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

    def __eq__(self, other):
        if getattr(self, 'polarity') != getattr(other, 'polarity'):
            return False
        
        for key in ['kn', 'ks']:
            if len(getattr(self, key)) != len(getattr(other, key)):
                return False
            arr_eq = np.isclose(getattr(self, key), getattr(other, key), rtol=1e-8)
            if False in arr_eq:
                return False
        return True


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

    def __eq__(self, other):
        if getattr(self, 'polarity') != getattr(other, 'polarity'):
            return False
        
        for key in ['knl', 'ksl']:
            if len(getattr(self, key)) != len(getattr(other, key)):
                return False
            arr_eq = np.isclose(getattr(self, key), getattr(other, key), rtol=1e-8)
            if False in arr_eq:
                return False
        return True


@dataclass(eq=False)
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
    
    @property
    def k1s(self):
        return self.ks[1]

    @k1s.setter
    def k1s(self, k1s: float):
        self.ks[1] = k1s
    
    

@dataclass(eq=False)
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
    
    @property
    def k2s(self):
        return self.ks[2]

    @k2s.setter
    def k2s(self, k2s: float):
        self.ks[2] = k2s


@dataclass(eq=False)
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
    
    @property
    def k3s(self):
        return self.ks[3]

    @k3s.setter
    def k3s(self, k3s: float):
        self.ks[3] = k3s


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
