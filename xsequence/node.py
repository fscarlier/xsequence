import xdeps 
import numpy as np
import xsequence.elements as xe
from dataclasses import dataclass
from scipy.spatial.transform import Rotation
from typing import List, Dict
from numpy.typing import ArrayLike


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
                 alignment_errors: AlignmentErrors = AlignmentErrors(),
                 magnetic_errors: MagneticErrors = MagneticErrors(),
                ):
        self.element_name = element_name
        self.element_number = element_number
        self.length = length
        self.pos_anchor  = pos_anchor
        self.location  = location
        self.reference = reference
        self.alignment_errors = alignment_errors
        self.magnetic_errors = magnetic_errors

    @property
    def start(self):
        return self.positions['start']
    
    @property
    def end(self):
        return self.positions['end']
    
    @property
    def positions(self):
        return self.calculate_positions()

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
            position['start'] = loc - self.length/2
            position['center'] = loc
            position['end'] = loc + self.length/2
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

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.__dict__ if x != 'name'])
        return f'{self.__class__.__name__}({self.element_name}{content})'


class Sequence:
    """ Class to describe sequence of Nodes in accelerator lattice """
    def __init__(self, 
                 name:str, 
                 elements:Dict[str, xe.BaseElement], 
                 nodes: List[Node], 
                 ):
        self.name = name
        self.nodes = nodes
        self.elements = elements
        self.update_nodes()

    @property
    def names(self) -> list:
        return [node.element_name for node in self.nodes]
    
    @property
    def positions(self) -> list:
        return self.get_positions()

    @property
    def coordinates(self) -> list:
        return self.get_coordinates()

    def get_coordinates(self, error_anchor:str = 'center') -> list:
        return [node.coordinates[error_anchor] for node in self.nodes] 

    def get_positions(self, pos_anchor:str = 'center') -> list:
        return [node.positions[pos_anchor] for node in self.nodes] 
    
    def _set_lengths_of_nodes(self):
        temp_dict = {}
        self.length_mgr=xdeps.Manager()
        self.eref = self.length_mgr.ref(self.elements, 'elements')
        self.nref = self.length_mgr.ref(self.nodes, 'nodes')
        for idx, node in enumerate(self.nodes):
            self.nref[idx].length = self.eref[node.element_name].length
            #set element number
            name = node.element_name
            if name in temp_dict:
                temp_dict[name] += 1
            else:
                temp_dict[name] = 1
            node.element_number = temp_dict[name]
        
    def _check_negative_drifts(self):
        start = np.array([node.positions['start'] for node in self.nodes]) 
        end = np.array([node.positions['end'] for node in self.nodes])
        end = np.insert(end, 0, 0)[:-1]
        assert np.all(start - end >= 0), "Negative drift detected"

    def _order_nodes_by_position(self):
        """ Order nodes depending on longitudinal position in accelerator """
        _, nodes = zip(*sorted(zip(self.get_positions(), self.nodes))) 
        self.nodes = list(nodes) 

    def update_nodes(self):
        self._set_lengths_of_nodes()
        self._order_nodes_by_position()
        self._check_negative_drifts()