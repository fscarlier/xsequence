import xdeps 
import numpy as np
import xsequence.elements as xe
from dataclasses import dataclass
from scipy.spatial.transform import Rotation
from typing import List, Dict
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


class Lattice:
    """ Class to describe sequence of Nodes in accelerator lattice """
    def __init__(self, 
                 name:str, 
                 elements:dict, 
                 sequence: NodesList,
                 key: str,
                 beam: Beam,
                 global_variables: dict = {}, 
                 ):
        
        self.name = name
        self.beam = beam
        self.elements = elements
        self.globals = global_variables
        
        if key == 'line':
            self.sequence = self._set_sequence_from_line(sequence)
        elif key == 'sequence':
            self.sequence = self._order_nodes_by_position(sequence)
        
        self.dep_mgr=xdeps.Manager()
        self._elements = self.dep_mgr.ref(self.elements, 'elements')
        self._sequence = self.dep_mgr.ref(self.sequence, 'sequence')
        self._globals = self.dep_mgr.ref(self.globals, 'globals')
        
        self._set_lengths_of_nodes()
        self._set_element_number()
    
    def get_drifts(self) -> NodesList:
        """ Get list of elements matching given classes """
        self._set_line()
        return NodesList([node for node in self.sequence if type(self.elements[node.element_name]) is xe.Drift])

    def get_class(self, class_types: list) -> NodesList:
        """ Get list of elements matching given classes """
        return NodesList([node for node in self.sequence if type(self.elements[node.element_name]) in class_types])

    def get_total_length(self) -> float:
        return self.sequence._get_total_length()

    def _update_cavity_energy(self):
        for cavity_node in self.get_class(class_types=[xe.RFCavity]):
            self.elements[cavity_node.element_name].energy = self.beam.energy

    def _update_harmonic_number(self):
        for cav in self.get_class(class_types=[xe.RFCavity]):
            # Approximation for ultra-relativistic electrons
            self.sequence[cav].harmonic_number = int(self.sequence[cav].frequency*1e6/(scipy.constants.c/self.get_total_length()))

    def _set_lengths_of_nodes(self):
        for idx, node in enumerate(self.sequence):
            name = node.element_name
            self._sequence[idx].length = self.elements[name].length
        
    def _order_nodes_by_position(self, nodes) -> NodesList:
        """ Order nodes depending on longitudinal position in accelerator """
        _, nodes = zip(*sorted(zip([node.positions['center'] for node in nodes], nodes))) 
        return NodesList(nodes)
    
    def _set_sequence_from_line(self, nodes) -> NodesList:
        """ Calculate longitudinal positions of elements from line representation """
        previous_end = 0.0
        for node in nodes:
            node.length = self.elements[node.element_name].length
            node.location = previous_end + node.length/2. 
            previous_end += node.length
        return NodesList([k for k in nodes if not isinstance(self.elements[k], xe.Drift)])
    
    def _check_negative_drifts(self):
        start = np.array( self.sequence.get_positions(pos_anchor='start') )
        end = np.array( self.sequence.get_positions(pos_anchor='end') )
        end = np.insert(end, 0, 0)[:-1]
        assert np.all(start - end >= 0), "Negative drift detected"
        
    def _set_line(self):
        line, line_elements = self._get_line()
        self._line = line
        self._line_elements = line_elements

    def _get_line(self):
        """ Convert sequence representation to line representation including drifts """
        previous_end = self.sequence[0].start
        drift_count = 0
        nodes_with_drifts = NodesList()
        elements_with_drifts = self.elements.copy()
        for node in self.sequence:
            node_start = node.start
            drift_length = node_start-previous_end
            if drift_length > 1e-10:
                drift_pos = previous_end + drift_length/2.
                drift_name = f'drift_{drift_count}'
                elements_with_drifts[drift_name] = xe.Drift(drift_name, length=drift_length)
                nodes_with_drifts.append(Node(element_name=drift_name, length=drift_length, location=drift_pos))
                drift_count += 1
            elif node_start < previous_end-1e-9: # Tolerance for rounding
                raise ValueError(f'Negative drift at element {node.element_name} {node.element_number}')

            nodes_with_drifts.append(node)
            previous_end = node.end
        return nodes_with_drifts, elements_with_drifts
    
    def _set_element_number(self):
        temp_dict = {}
        for idx, node in enumerate(self.sequence):
            name = node.element_name
            if name in temp_dict:
                temp_dict[name] += 1
            else:
                temp_dict[name] = 1
            self.sequence[idx].element_number = temp_dict[name]
    
    def update_sequence(self):
        # self._order_nodes_by_position(nodes)
        self._set_element_number()
        self._check_negative_drifts()

    def convert_sbend_to_rbend(self):
        """ Convert all sbends to rbends in elements """
        for key in self.elements:
            if isinstance(self.elements[key], xe.SectorBend):
                self.elements[key] = self.elements[key].convert_to_rbend()

    def convert_rbend_to_sbend(self):
        """ Convert all rbends to sbends in elements """
        for key in self.elements:
            if isinstance(self.elements[key], xe.RectangularBend):
                self.elements[key] = self.elements[key].convert_to_sbend()


    #Slicing needs to be checked!! 
    #   - New reference needs to be created 
    #   - Slicing should not take place as element methods 
    def _slice_lattice(self):
        thin_list = [el.slice_element() for name, el in self.sequence.items()]
        thin_list = [item for sublist in thin_list for item in sublist]
        return {el.name:el for el in thin_list}
