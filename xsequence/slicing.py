# copyright #################################### #
# This file is part of the Xsequence Package.    #
# Copyright (c) CERN, 2022.                      #
# ############################################## #


class UndefinedSlicingMethod(Exception):
    """Exception raised for trying to define kn/ks for Quadrupole, Sextupole, Octupole."""
    def __init__(self, method: str):
        self.method = method
        self.message = f'Slicing method undefined: {method}'
        super().__init__(self.message)


def get_teapot_slicing_positions(element) -> list:
    if element.num_slices == 1:
        return [0.0]
    else:
        delta = element.length*(1/(2*element.num_slices + 2))
        separation = element.length*(element.num_slices/(element.num_slices**2 - 1))
        thin_locations =  [-element.length/2 + delta]
        for i in range(element.num_slices-1):
            thin_locations.append(thin_locations[-1] + separation)
        return thin_locations


def get_uniform_slicing_positions(element) -> list:
    if element.num_slices == 1:
        return [0.0]
    else:
        separation = element.length/(element.num_slices - 1)
        thin_locations =  [-element.length/2]
        for i in range(element.num_slices-1):
            thin_locations.append(thin_locations[-1] + separation)
        return thin_locations


def get_slice_positions(element, method: str ='teapot') -> list:
    if method == 'teapot':
        return get_teapot_slicing_positions(element)
    elif method == 'uniform':
        return get_uniform_slicing_positions(element)
    else:
        raise UndefinedSlicingMethod(method)

