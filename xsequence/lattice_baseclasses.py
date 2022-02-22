"""
Module xsequence.lattice_baseclasses
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element dataclasses for particle accelerator elements.
"""

from collections import OrderedDict
import numpy as np
from typing import List
from dataclasses import dataclass
from scipy.spatial.transform import Rotation
from numpy.typing import ArrayLike


@dataclass
class Beam:
    energy: float 
    particle: str


@dataclass
class MagneticErrors:
    knl_errors: np.ndarray = np.zeros(6) 
    ksl_errors: np.ndarray = np.zeros(6) 


@dataclass
class AlignmentErrors:
    error_anchor: str = 'start' 
    translations: np.ndarray = np.zeros(3) 
    rotations: np.ndarray = np.zeros(3)
    
    def rotate(self, xyz_vector: ArrayLike) -> np.ndarray:
        xyz_vector = np.array(xyz_vector)
        rotation_matrix = Rotation.from_euler('xyz', self.rotations)
        return rotation_matrix.apply(xyz_vector)
    
    def __repr__(self) -> str:
        content = ", ".join([f"{x}={getattr(self, x)}" for x in self.__dict__])
        return f'{self.__class__.__name__}({content})'


class Node:
    """ Node class containing local element information """    
    def __init__(self, 
                 element_name: str, 
                 element_number: int = 0,
                 pos_anchor: str = 'center',
                 length: float = 0.0, 
                 location: float = 0.0,
                 reference: float = 0.0,
                 reference_element: str = '',
                 alignment_errors: AlignmentErrors = AlignmentErrors(),
                 magnetic_errors: MagneticErrors = MagneticErrors(),
                ):
        self.element_name = element_name
        self.element_number = element_number
        self.length = length
        self.pos_anchor  = pos_anchor
        self.location  = location
        self.reference = reference
        self.reference_element = reference_element
        self.alignment_errors = alignment_errors
        self.magnetic_errors = magnetic_errors

    @property
    def start(self):
        return self.calculate_positions()['start']
    
    @property
    def end(self):
        return self.calculate_positions()['end']
    
    @property
    def position(self):
        return self.calculate_positions()['center']

    @property
    def coordinates(self):
        return self.calculate_coordinates()

    def calculate_positions(self):
        position = {}
        if self.pos_anchor == 'start':
            loc = self.location + self.reference
            position['start'] = loc
            position['center'] = loc + self.length/2
            position['end'] = loc + self.length
        elif self.pos_anchor == 'center':
            loc = self.location + self.reference
            position['start'] = loc - self.length/2.
            position['center'] = loc
            position['end'] = loc + self.length/2.
        elif self.pos_anchor == 'end':
            loc = self.location + self.reference
            position['start'] = loc - self.length
            position['center'] = loc - self.length/2
            position['end'] = loc
        return position

    def _calc_misalign(self, place: float) -> np.ndarray:
        return self.alignment_errors.translations + self.alignment_errors.rotate([0, 0, place]) - np.array([0, 0, place])

    def calculate_coordinates(self):
        coordinates = {}
        if self.alignment_errors.error_anchor == 'start':
            coordinates['center'] = self._calc_misalign(self.length/2)
            coordinates['end']    = self._calc_misalign(self.length)
        elif self.alignment_errors.error_anchor == 'center':                                                                                   
            coordinates['start']  = self._calc_misalign(-self.length/2)
            coordinates['end']    = self._calc_misalign( self.length/2)
        elif self.alignment_errors.error_anchor == 'end':                                                                                    
            coordinates['start']  = self._calc_misalign(-self.length)
            coordinates['center'] = self._calc_misalign(-self.length/2)
        return coordinates
    
    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        for k in self.__dict__:
            if getattr(self, k) != getattr(other, k):
                if isinstance(getattr(self, k), float):
                    f1 = getattr(self, k) 
                    f2 = getattr(other, k)    
                    rel_diff = (f2-f1)/f1
                    if rel_diff > 1e-19:
                        return False
                else:
                    return False
        return True

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.__dict__ if x != 'name'])
        return f'{self.__class__.__name__}({self.element_name}{content})'


class NodesList(List):
    @property
    def names(self) -> list:
        return [node.element_name for node in self]
    
    @property
    def positions(self) -> list:
        return self.get_positions()
    
    @property
    def lengths(self) -> list:
        return [node.length for node in self]

    @property
    def coordinates(self) -> list:
        return self.get_coordinates()
    
    def get_positions(self, pos_anchor:str = 'center') -> list:
        return [node.positions[pos_anchor] for node in self] 

    def get_coordinates(self, error_anchor:str = 'center') -> list:
        return [node.coordinates[error_anchor] for node in self] 

    def find_elements(self, pattern):
        if pattern.startswith('*'):
            return NodesList([node for node in self if node.element_name.endswith(pattern[1:])])
        elif pattern.endswith('*'):
            return NodesList([node for node in self if node.element_name.startswith(pattern[:-1])])
        else:
            return NodesList([node for node in self if pattern in node.element_name])

    def get_range_s(self, start_location: float, end_location: float):
        start_idx = next(idx for idx, node in enumerate(self) if node.start > start_location)
        stop_idx = 1 + next(idx for idx, node in enumerate(self) if node.end > end_location)
        return self[start_idx:stop_idx]
    
    def _get_total_length(self):
        return self[-1].end

    def __repr__(self):
        return f"{self.names}"

