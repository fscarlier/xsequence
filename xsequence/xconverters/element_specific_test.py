import xsequence.elements_dataclasses as xed
from typing import List


    


class Node:
    """ Node class containing local element information """    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.element_number = kwargs.pop('element_number', None)
        self.position_data = kwargs.pop('position_data', xed.ElementPosition(**{k:kwargs[k] for k in xed.ElementPosition.INIT_PROPERTIES if k in kwargs})) 

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.__dict__ if x != 'name'])
        return f'{self.__class__.__name__}({self.name}{content})'


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
        element_dict = {}
        for node in self.nodes:
            name = node.name
            if name in element_dict:
                element_dict[name] += 1
            else:
                element_dict[name] = 1
            node.element_number = element_dict[name]
