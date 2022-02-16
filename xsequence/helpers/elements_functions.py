from typing import List, Tuple
import xsequence.elements_dataclasses as xed


def _property_factory(data_type, api_property_name, docstring=None):
    def getter(self):
        return self.__getattribute__(data_type).__getattribute__(api_property_name)

    def setter(self, value):
        self.__getattribute__(data_type).__setattr__(api_property_name, value)

    return property(getter, setter, doc=docstring)


def get_teapot_slicing_positions(position: xed.ElementPosition, num_slices: int):
    """
    TODO: Should return ElementPosition objects of course!
    Currently make do with distance to 0 refernce only..
    """
    if num_slices == 1:
        return [position.position], position.length
    elif num_slices > 1:
        delta = position.length*(1/(2*num_slices + 2))
        separation = position.length*(num_slices/(num_slices**2 - 1))
        thin_positions =  [position.start+delta]
        for i in range(num_slices-1):
            thin_positions.append(thin_positions[-1] + separation)
        return thin_positions, position.length / num_slices 


def get_uniform_slicing_positions(position: xed.ElementPosition, num_slices: int):
    """
    TODO: Should return ElementPosition objects of course!
    Currently make do with distance to 0 refernce only..
    """
    if num_slices == 1:
        return [position.position], position.length
    elif num_slices > 1:
        separation = position.length/(num_slices - 1)
        thin_positions =  [position.start]
        for i in range(num_slices-1):
            thin_positions.append(thin_positions[-1] + separation)
        return thin_positions, position.length / num_slices 


def get_id_data(id_class=xed.ElementID, **kwargs):
    return id_class(**{k:kwargs[k] for k in id_class.INIT_PROPERTIES if k in kwargs})
        
def get_parameter_data(parameter_class=xed.ElementParameterData, **kwargs):
    return parameter_class(**{k:kwargs[k] for k in parameter_class.INIT_PROPERTIES if k in kwargs})
        
def get_position_data(position_class=xed.ElementPosition, **kwargs):
    return position_class(**{k:kwargs[k] for k in position_class.INIT_PROPERTIES if k in kwargs})

def get_aperture_data(aperture_class=xed.ApertureData, **kwargs):
    return aperture_class(**{k:kwargs[k] for k in aperture_class.INIT_PROPERTIES if k in kwargs})

def get_pyat_data(pyat_class=xed.PyatData, **kwargs):
    return pyat_class(**{k:kwargs[k] for k in pyat_class.INIT_PROPERTIES if k in kwargs})
