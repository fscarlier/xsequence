"""
Module fsf.base_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element dataclasses for particle accelerator elements.
"""

from typing import List, Optional
from dataclasses import dataclass, field
import numpy as np

 
class BaseElementData: 
    def __iter__(self):
        for key in self.INIT_PROPERTIES:
            yield key, getattr(self, key)


@dataclass
class ElementID(BaseElementData):
    INIT_PROPERTIES = ['slot_id', 'assembly_id']
    slot_id: Optional[int] = None
    assembly_id: Optional[int] = None

    def __post_init__(self):
        if self.slot_id == 0.0: self.slot_id = None
        if self.assembly_id == 0.0: self.assembly_id = None

@dataclass
class ElementPosition(BaseElementData):
    """ Dataclass containing all relevant information about element position in [m] """
    INIT_PROPERTIES = ['length', 'location', 'reference', 'reference_element', 'mech_sep']
    length: float = 0.0
    _length: float = field(init=False, repr=False, default=0.0)
    location: float = 0.0
    _location: float = field(init=False, repr=False, default=0.0)
    reference: float = 0.0
    _reference: float = field(init=False, repr=False, default=0.0)
    reference_element: str = ''
    # tilt: float = 0.0
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
class ApertureData(BaseElementData):
    """Represents an aperture for elements"""
    INIT_PROPERTIES = ['aperture_size', 'aperture_offset']
    aperture_size: List = field(default_factory=lambda: [0.0, 0.0])
    aperture_offset: List = field(default_factory=lambda: [0.0, 0.0])


@dataclass
class EllipticalAperture(ApertureData):
    INIT_PROPERTIES = ['aperture_type']
    aperture_type: Optional[str] = 'elliptical'

    def __post_init__(self):
        self.INIT_PROPERTIES = self.INIT_PROPERTIES + super().INIT_PROPERTIES


@dataclass
class RectangularAperture(ApertureData):
    """Rectangular aperture dataclass. Aperture_size : [left, right, bottom, up]"""
    INIT_PROPERTIES = ['aperture_type']
    aperture_type: Optional[str] = 'rectangular'

    def __post_init__(self):
        self.INIT_PROPERTIES = self.INIT_PROPERTIES + super().INIT_PROPERTIES
        if len(self.aperture_size) == 4:
            self.reset_offset_and_size_from_4_array()

    def reset_offset_and_size_from_4_array(self):
        x_offset = (self.aperture_size[0] + self.aperture_size[1]) / 2.
        y_offset = (self.aperture_size[2] + self.aperture_size[3]) / 2.
        self.aperture_offset = [x_offset, y_offset]
        self.aperture_size = [x_offset - self.aperture_size[0], y_offset - self.aperture_size[2]]

    def get_4_array(self):
        aperture_size_data = [self.aperture_offset[0] - self.aperture_size[0],
                            self.aperture_offset[0] + self.aperture_size[0],
                            self.aperture_offset[1] - self.aperture_size[1],
                            self.aperture_offset[1] + self.aperture_size[1]]
        return aperture_size_data


@dataclass
class BendData(BaseElementData):
    """ Bend strength dataclass """
    INIT_PROPERTIES = ['angle', 'e1', 'e2', 'k0']
    angle: float = 0.0
    e1: float = 0.0
    e2: float = 0.0
    k0: Optional[float] = 0.0  


@dataclass
class SolenoidData(BaseElementData):
    """ Solenoid strength dataclass """
    INIT_PROPERTIES = ['ks']
    ks: float = 0.0


@dataclass
class ThinSolenoidData(BaseElementData):
    """ Solenoid strength dataclass """
    INIT_PROPERTIES = ['ksi']
    ksi: float = 0.0


@dataclass
class DipoleEdgeData(BaseElementData):
    """ Dipole edge strength dataclass """
    INIT_PROPERTIES = ['h', 'e1', 'side']
    h: float 
    e1: float 
    side: str 
    
    def __post_init__(self):
        assert self.side in ('entrance', 'exit'), f"Invalid side Attribute for DipoleEdgeData"


@dataclass
class MultipoleStrengthData(BaseElementData):
    INIT_PROPERTIES = ['kn', 'ks', 'polarity']
    kn: List = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0])  
    ks: List = field(default_factory=lambda: [0.0, 0.0, 0.0, 0.0]) 
    polarity: int = None  

    @property
    def kn(self):
        self._update_arrays()
        return self.kn

    @property
    def ks(self):
        self._update_arrays()
        return self.ks

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
class ThinMultipoleStrengthData(BaseElementData):
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


@dataclass
class QuadrupoleData(BaseElementData):
    INIT_PROPERTIES = ['k1', 'k1s', 'kmax', 'kmin']
    k1: float = 0.0
    k1s: float = 0.0
    kmax: float = None
    kmin: float = None
    
    def __post_init__(self):
        if self.kmax == 0.0: self.kmax = None
        if self.kmin == 0.0: self.kmin = None

    @property
    def kn(self):
        return np.array([0.0, self.k1]) 

    @property
    def ks(self):
        return np.array([0.0, self.k1s]) 


@dataclass
class SextupoleData(BaseElementData):
    INIT_PROPERTIES = ['k2', 'k2s', 'kmax', 'kmin']
    k2: float = 0.0
    k2s: float = 0.0
    kmax: float = None
    kmin: float = None

    def __post_init__(self):
        if self.kmax == 0.0: self.kmax = None
        if self.kmin == 0.0: self.kmin = None

    @property
    def kn(self):
        return np.array([0.0, 0.0, self.k2]) 

    @property
    def ks(self):
        return np.array([0.0, 0.0, self.k2s]) 


@dataclass
class OctupoleData(BaseElementData):
    INIT_PROPERTIES = ['k3', 'k3s', 'kmax', 'kmin']
    k3: float = 0.0
    k3s: float = 0.0
    kmax: float = None
    kmin: float = None

    def __post_init__(self):
        if self.kmax == 0.0: self.kmax = None
        if self.kmin == 0.0: self.kmin = None

    @property
    def kn(self):
        return np.array([0.0, 0.0, 0.0, self.k3]) 

    @property
    def ks(self):
        return np.array([0.0, 0.0, 0.0, self.k3s]) 


@dataclass
class RFCavityData(BaseElementData):
    INIT_PROPERTIES = ['voltage', 'frequency', 'lag']
    voltage: float = 0.0  
    frequency: float = 0.0 
    lag: float = 0.0 


@dataclass
class KickerData(BaseElementData):
    INIT_PROPERTIES = ['hkick', 'vkick', 'kmax', 'kmin']
    kmax: float = None 
    kmin: float = None 
    hkick: float = None 
    vkick: float = None 


@dataclass
class HKickerData(KickerData):
    INIT_PROPERTIES = ['kick', 'kmin', 'kmax']
    kick: float = None 


@dataclass
class VKickerData(KickerData):
    INIT_PROPERTIES = ['kick', 'kmin', 'kmax']
    kick: float = None 


@dataclass
class PyatData(BaseElementData):
    """ Specifc PyAT only data dataclass """
    INIT_PROPERTIES = ['NumIntSteps', 'PassMethod']
    NumIntSteps: int = None
    PassMethod: str = None
