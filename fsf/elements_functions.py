from typing import List
import fsf.elements_dataclasses as xed


def _property_factory(data_type, api_property_name, docstring=None):
    def getter(self):
        return self.__getattribute__(data_type).__getattribute__(api_property_name)

    def setter(self, value):
        self.__getattribute__(data_type).__setattr__(api_property_name, value)

    return property(getter, setter, doc=docstring)


def get_teapot_slicing_positions(position: xed.ElementPosition, num_slices: int) -> List:
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
