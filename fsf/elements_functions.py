from typing import List
from fsf.elements import BaseElement
import fsf.elements_dataclasses as xed


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


def get_sliced_multipole_strengths(strength: xed.MultipoleStrengthData, num_slices: int) -> List:
    knl = strength.knl / num_slices
    ksl = strength.ksl / num_slices
    return xed.ThinMultipoleStrengthData(knl=knl, ksl=ksl, polarity=strength.polarity)


def get_sliced_bend_strength(bend: xed.BendData, num_slices: int) -> List:
    knl = [bend.angle / num_slices]
    return xed.ThinMultipoleStrengthData(knl=knl)


def get_sliced_solenoid_strength(solenoid_data: xed.SolenoidData, num_slices: int) -> List:
    ksi = solenoid_data.ksi/num_slices
    return xed.ThinSolenoidData(ksi=ksi)
