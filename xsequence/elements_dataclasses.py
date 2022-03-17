"""
Module xsequence.base_elements
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
class ElementParameterData(BaseElementData): 
    INIT_PROPERTIES = ['polarity', 'calibration', 'kmax', 'kmin', 'tilt']
    polarity: int = 0.0
    calibration: float = 0.0
    kmax: float = None
    kmin: float = None
    tilt: float = 0.0
    
    def __post_init__(self):
        if self.kmax == 0.0: self.kmax = None
        if self.kmin == 0.0: self.kmin = None


@dataclass
class ElementPosition(BaseElementData):
    """ Dataclass containing all relevant information about element position in [m] """
    INIT_PROPERTIES = ['length', 'radiation_length', 'location', 'reference', 'reference_element', 'mech_sep'] 
    length: float = 0.0
    radiation_length: float = 0.0
    _length: float = field(init=False, repr=False, default=0.0)
    location: float = 0.0
    _location: float = field(init=False, repr=False, default=0.0)
    reference: float = 0.0
    _reference: float = field(init=False, repr=False, default=0.0)
    reference_element: str = ''
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
    INIT_PROPERTIES = ['aperture_size', 'aperture_offset', 'aper_vx', 'aper_vy'] 
    aperture_size: List = field(default_factory=lambda: [0.0, 0.0])
    aperture_offset: List = field(default_factory=lambda: [0.0, 0.0])
    aper_vx: float = None
    aper_vy: float = None


@dataclass
class CircularAperture(ApertureData):
    INIT_PROPERTIES = ['aperture_type'] + ApertureData.INIT_PROPERTIES
    aperture_type: Optional[str] = 'circular'


@dataclass
class EllipticalAperture(ApertureData):
    INIT_PROPERTIES = ['aperture_type'] + ApertureData.INIT_PROPERTIES
    aperture_type: Optional[str] = 'elliptical'


@dataclass
class RectangularAperture(ApertureData):
    """Rectangular aperture dataclass. Aperture_size : [left, right, bottom, up]"""
    INIT_PROPERTIES = ['aperture_type'] + ApertureData.INIT_PROPERTIES
    aperture_type: Optional[str] = 'rectangular'

    def __post_init__(self):
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
class AlignmentError(BaseElementData):
    INIT_PROPERTIES = ['kn_err', 'ks_err'] 
    dx: float= 0.0  # Horizontal displacement [m]
    dy: float= 0.0  # Vertical displacement [m]
    ds: float= 0.0  # Longitudinal displacement [m] 
    dphi: float= 0.0    # Rotation about x-axis [rad] 
    dtheta: float= 0.0  # Rotation about y-axis [rad]
    dpsi: float= 0.0    # Rotation about s-axis [rad]


@dataclass
class MultipoleError(BaseElementData):
    INIT_PROPERTIES = ['kn_err', 'ks_err'] 
    kn_err: List = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 0.0]))  
    ks_err: List = field(default_factory=lambda: np.array([0.0, 0.0, 0.0, 0.0])) 


@dataclass
class PyatData(BaseElementData):
    """ Specifc PyAT only data dataclass """
    INIT_PROPERTIES = ['NumIntSteps', 'PassMethod'] 
    NumIntSteps: int = None
    PassMethod: str = None
