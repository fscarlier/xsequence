"""
Module xsequence.lattice_baseclasses
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element dataclasses for particle accelerator elements.
"""

from collections import OrderedDict
from dataclasses import dataclass
import xsequence.elements as xe
from typing import List, Tuple

def _key_to_idx_slice(names, key):
    if key.start:
        start_idx = names.index(key.start)
    else:
        start_idx = 0
    if key.stop:
        stop_idx = names.index(key.stop)
    else:
        stop_idx = len(names)
    return slice(start_idx, stop_idx)


class ElementDict(OrderedDict):
    @property
    def names(self):
        return [self[element].name for element in self]
    
    @property
    def positions(self):
        return [self[element].position_data.position for element in self]
    
    @property
    def lengths(self):
        return [self[element].position_data.length for element in self]

    def get_last_element(self):
        return self[self.names[-1]]    
    
    def get_class(self, class_type: List[str]) -> List[xe.BaseElement]:
        """ Get list of elements matching given class """
        return ElementDict({name:self[name] for name in self if self[name].__class__.__name__ in class_type})

    def find_elements(self, pattern):
        if pattern.startswith('*'):
            return ElementDict({name:self[name] for name in self if name.endswith(pattern[1:])})
        elif pattern.endswith('*'):
            return ElementDict({name:self[name] for name in self if name.startswith(pattern[:-1])})
        else:
            return ElementDict({name:self[name] for name in self if pattern in name})

    def _get_names(self):
        return list(self.keys())
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            names = self._get_names()
            if isinstance(key.start, str):
                key = _key_to_idx_slice(names, key)
            names = names[key]
            return ElementDict({name:self[name] for name in names})
        else:
            if isinstance(key, int):
                return self[self.names[key]]
            else:
                return super().__getitem__(key)

    def __repr__(self):
        return f"{self.names}"


@dataclass
class Beam:
    energy: float 
    particle: str



class Nodes:
    """ Class to describe sequence of Nodes in accelerator lattice """
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, nodes):
        self._nodes = nodes
        self._order_nodes_by_position()
        self._set_ele_number()
    
    @property
    def names(self):
        return [node.name for node in self.nodes]
    
    @property
    def positions(self):
        return [node.position_data.position for node in self.nodes]

    def _order_nodes_by_position(self):
        """ Order nodes depending on longitudinal position in accelerator """
        _, nodes = zip(*sorted(zip(self.positions, self.nodes)))                    
        self._nodes = list(nodes) 

    def _set_ele_number(self):
        """ Set element number relating to occurence of element in lattice """
        temp_dict = {}
        for node in self.nodes:
            name = node.name
            if name in temp_dict:
                temp_dict[name] += 1
            else:
                temp_dict[name] = 1
            node.element_number = temp_dict[name]


class ElementsLattice:
    def __init__(self, elements_dict: ElementDict, nodes: Nodes):
        self.elements_dict = elements_dict
        self.nodes = nodes
    

class Line(ElementsLattice):
    def _set_positions(self):
        """ Calculate longitudinal positions of elements from line representation """
        previous_end = 0.0
        for name, element in self.items():
            element.position_data.set_position(location=previous_end+element.length/2.) 
            previous_end += element.length

    def _get_sequence(self):
        self._set_positions()
        return Sequence({k:self[k] for k in self if not isinstance(self[k], xe.Drift)})


class Sequence(ElementsLattice):
    def _get_line(self):
        """ Convert sequence representation to line representation including drifts """
        previous_end = self[self._get_names()[0]].position_data.start
        drift_count = 0
        line_w_drifts = OrderedDict()
        for name, element in self.items():
            element_start = element.position_data.start
            if element_start > previous_end:
                drift_length = element_start-previous_end
                if drift_length > 1e-10:
                    drift_pos = previous_end + drift_length/2.
                    drift_name = f'drift_{drift_count}'
                    line_w_drifts[drift_name] = xe.Drift(drift_name, length=drift_length, location=drift_pos)
                    drift_count += 1
            elif element_start < previous_end-1e-9: # Tolerance for rounding
                raise ValueError(f'Negative drift at element {element.name}')

            line_w_drifts[name] = element
            previous_end = element.position_data.end
        return Line(line_w_drifts)