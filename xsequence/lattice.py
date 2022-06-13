import math, copy
import xdeps 
import numpy as np
import scipy.constants
import xsequence.elements as xe
from xsequence import slicing
from xsequence.lattice_baseclasses import Node, NodesList, Beam


class Lattice:
    """ Class to describe an accelerator lattice """
    def __init__(self, 
                 name:str, 
                 elements:dict, 
                 sequence: NodesList,
                 beam: Beam ,
                 key: str = 'sequence',
                 global_variables: dict = {},
                 order_nodes: str = False, 
                 ):
        
        self.name = name
        self.beam = beam
        
        if order_nodes:
            sequence = self._order_nodes_by_position(sequence)

        if key == 'line':
            elements, sequence = self._get_sequence_from_line(sequence, elements)
        
        self._data_globals  = global_variables
        self._data_elements = elements
        self._data_sequence = sequence
        
        self.dep_mgr=xdeps.Manager()
        self._elements = self.dep_mgr.ref(self._data_elements, 'elements')
        self._sequence = self.dep_mgr.ref(self._data_sequence, 'sequence')
        self._globals  = self.dep_mgr.ref(self._data_globals , 'globals' )
        self._math  = self.dep_mgr.ref(math, 'math' )
        
        self.elements = xdeps.madxutils.Mix(self._data_elements, self._elements)
        self.sequence = xdeps.madxutils.Mix(self._data_sequence, self._sequence)
        self.globals  = xdeps.madxutils.Mix(self._data_globals , self._globals )
        
        self._set_lengths_of_nodes()
        self._set_element_number()
    
    def get_drifts(self) -> NodesList:
        """ Get list of Drift elements """
        self._set_line()
        return NodesList([node for node in self.sequence if type(self.elements[node.element_name]) is xe.Drift])

    def get_class(self, class_types: list) -> NodesList:
        """ Get list of elements matching given classes """
        return NodesList([node for node in self.sequence if type(self.elements[node.element_name]) in class_types])

    def get_total_length(self) -> float:
        return self.sequence._v._get_total_length()

    def _update_cavity_energy(self, force=True):
        """ Update the energy of RF cavities. Needed for pyat """
        for cavity_node in self.get_class(class_types=[xe.RFCavity]):
            element = self.elements[cavity_node.element_name]
            if force: 
                element.energy = self.beam.energy
            else: 
                if element.energy in [0.0, None]: 
                    element.energy = self.beam.energy

    def _update_harmonic_number(self, force=True):
        """ Update the harmonic number of RF cavities using ultra-relativistic approximation. Needed for pyat """
        for cavity_node in self.get_class(class_types=[xe.RFCavity]):
            element = self.elements[cavity_node.element_name]
            if force: 
                element.harmonic_number = int(element.frequency*1e6/(scipy.constants.c/self.get_total_length()))
            else: 
                if element.harmonic_number in [0.0, None]: 
                    element.harmonic_number = int(element.frequency*1e6/(scipy.constants.c/self.get_total_length()))

    def _set_lengths_of_nodes(self):
        """ Set lengths of in nodes of sequence, as dependencies of element lengths """
        for idx, node in enumerate(self.sequence):
            name = node.element_name
            self.sequence[idx].length = self.elements[name].length
        
    def _order_nodes_by_position(self, nodes) -> NodesList:
        """ Order nodes depending on longitudinal position in accelerator """
        _, nodes = zip(*sorted(zip([node.position for node in nodes], nodes))) 
        return NodesList(nodes)
    
    def _get_sequence_from_line(self, nodes: NodesList, elements: dict) -> "Tuple[dict, NodesList]":
        """ Calculate longitudinal positions of elements from line representation """
        previous_end = 0.0
        for node in nodes:
            if node.length == 0.0:
                node.length = elements[node.element_name].length
            node.location = previous_end + node.length/2. 
            previous_end =  previous_end + node.length

        sequence = NodesList()
        sequence_elements = {}
        for node in nodes:
            if elements[node.element_name].__class__.__name__ != 'Drift':
                sequence.append(node)
                sequence_elements[node.element_name] = elements[node.element_name]
        return sequence_elements, sequence

    def _check_negative_drifts(self):
        """ Check any occurence of negative drifts in sequence """
        start = np.array( self.sequence.get_positions(pos_anchor='start') )
        end = np.array( self.sequence.get_positions(pos_anchor='end') )
        end = np.insert(end, 0, 0)[:-1]
        assert np.all(start - end >= 0), "Negative drift detected"
        
    def _set_line(self):
        """ Set line representation of sequence with explicit drifts """
        line, line_elements = self._get_line()
        self._line = line
        self._line_elements = line_elements

    def _get_line(self):
        """ Convert sequence representation to line representation including drifts """
        previous_end = self.sequence[0].start
        drift_count = 0
        nodes_with_drifts = NodesList()
        elements_with_drifts = self.elements._v.copy()
        for node in self.sequence:
            drift_length = node.start-previous_end
            if drift_length > 1e-10:
                drift_pos = previous_end + drift_length/2.
                drift_name = f'drift_{drift_count}'
                elements_with_drifts[drift_name] = xe.Drift(drift_name, length=drift_length)
                nodes_with_drifts.append(Node(element_name=drift_name, length=drift_length, location=drift_pos))
                drift_count += 1
            elif node.start < previous_end-1e-6: # Tolerance for rounding
                raise ValueError(f'Negative drift at element {node.element_name} {node.element_number}, {drift_length}, node = {node}')

            nodes_with_drifts.append(node)
            previous_end = node.end
        return nodes_with_drifts, elements_with_drifts
    
    def _set_element_number(self):
        """ Set element number to count multiple occurences of same element in sequence """
        temp_dict = {}
        for idx, node in enumerate(self.sequence):
            name = node.element_name
            if name in temp_dict:
                temp_dict[name] += 1
            else:
                temp_dict[name] = 1
            self.sequence[idx].element_number = temp_dict[name]
    
    def update_sequence(self):
        """ Update sequence and perform checks """
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

    def slice_lattice(self, method: str = 'teapot'):
        """ Slice lattice to obtain sequence of thin elements """
        self.thin_elements = {}
        self.thin_sequence = []
        self._thin_elements = self.dep_mgr.ref(self.thin_elements, 'thin_elements')
        self._thin_sequence = self.dep_mgr.ref(self.thin_sequence, 'thin_sequence')
        
        for idx, node in enumerate(self.sequence): 
            element = self.elements[node]
            
            if isinstance(element, xe.SectorBend):
                h = element.angle/element.length
                thin_name = f'{node.element_name}_sliced_entrance'
                self._thin_sequence.append(Node(thin_name, reference=node.position, location=node.start, length=0.0))
                self._thin_elements[thin_name] = xe.DipoleEdge(thin_name, side='entrance', h=h, edge_angle=element.e1)
    
            thin_positions = slicing.get_slice_positions(element, method=method)
            for idx, thin_pos in enumerate(thin_positions):
                thin_name = f'{node.element_name}_sliced_{idx}'
                self._thin_sequence.append(Node(thin_name, reference=node.position, location=thin_pos, length=0.0))
                self._thin_elements[thin_name] = element._get_thin_element()
            
            if isinstance(element, xe.SectorBend):
                h = element.angle/element.length
                thin_name = f'{node.element_name}_sliced_exit'
                self._thin_sequence.append(Node(thin_name, reference=node.position, location=node.end, length=0.0))
                self._thin_elements[thin_name] = xe.DipoleEdge(thin_name, side='exit', h=h, edge_angle=element.e2)
