from xsequence.elements_dataclasses import ElementPosition


class Node:
    """ Node class containing local element information """    
    length = xef._property_factory('position_data', 'length', docstring='Get and set length attribute')
    position = xef._property_factory('position_data', 'position', docstring='Get and set position attribute')
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.position_data = kwargs.pop('position_data', conv_utils.get_position_data(**kwargs)) 

    def _get_slice_positions(self, method='teapot'):
        if method == 'teapot':
            return xef.get_teapot_slicing_positions(self.position_data, self.num_slices)
        elif method == 'uniform':
            return xef.get_uniform_slicing_positions(self.position_data, self.num_slices)
     
    def _get_sliced_element(self, method='teapot', thin_class=None, **kwargs):
        thin_positions, rad_length = self._get_slice_positions(method=method)
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(thin_class(f'{self.name}_{idx}', radiation_length=rad_length, location=thin_pos, **kwargs) )
        return seq

    def _set_from_key(self, key, value):
        elif key in xed.ElementPosition.INIT_PROPERTIES:
            setattr(self.position_data, key, value)
        else:
            setattr(self, key, value)
    
    def get_dict(self):
        attr_dict = {}
        for k in self.__dict__:
            if isinstance(getattr(self, k), xed.BaseElementData):
                attr_dict.update(dict(getattr(self,k)))
            else:
                attr_dict[k] = getattr(self, k)
        return attr_dict

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        for k in self.__dict__:
            if k in ['kn', 'ks', 'knl', 'ksl']:
                if len(getattr(self, k)) != len(getattr(other, k)):
                    return False
                arr_eq = np.isclose(getattr(self, k), getattr(other, k), rtol=1e-8)
                if False in arr_eq:
                    return False
            else:
                if getattr(self, k) != getattr(other, k):
                    return False
        return True


class Nodes:
    def __init__(self, nodes):
        self.nodes = nodes

    @property
    def names(self):
        return [node.name for node in self.nodes]
    
    @property
    def positions(self):
        return [node.position_data.position for node in self.nodes]






class ElementNodes:
    def __init__(self, nodes, elements):
        self._nodes = nodes
        self._elements = elements
        self._reorder_nodes()

    @property
    def names(self):
        return [node.name for node in self.nodes]
    
    @property
    def positions(self):
        return [node.position_data.position for node in self.nodes]

    def _reorder_nodes(self):


    def find_ele_number(self):
        general_dict = {}
        element_dict = {}
        element_names = []
        for el in self._names:
            if el in element_dict:
                element_names.append((el, len(element_dict[el])))
                element_dict[el][len(element_dict[el])] = el+len(element_dict[el])
            else:
                element_names.append((el, 0))
                element_dict[el] = {0:el+'0'}
                general_dict[el] = el
        self._element_names = element_names
        self._element_dict = element_dict
        self._general_dict = general_dict
