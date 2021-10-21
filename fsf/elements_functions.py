from typing import List
import elements_dataclasses as xed
import elements as xe


def teapot_slicing(position: xed.ElementPosition, num_slices: int) -> List:
    delta = position.length*(1/(2*num_slices + 2))
    separation = position.length*(num_slices/(num_slices**2 - 1))
    thin_positions =  [position.start+delta]
    for i in range(num_slices-1):
        thin_positions.append(thin_positions[-1] + separation)
    return thin_positions 


def slice_element(element: xe.BaseElement, num_slices: int = 1, method:str = 'teapot') -> List:
    try: num_slices = element.int_steps
    except: AttributeError

    if element.length == 0:
        return [element]

    def _make_slices_multipoles(element, num_slices, knl_sliced=[0], ksl_sliced=[0]):
        thin_positions = element.teapot_slicing(num_slices)
        rad_length = element.length/num_slices
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(xe.ThinMultipole(f'{element.name}_{idx}', position=thin_pos, 
                                                                rad_length=rad_length, 
                                                                knl=knl_sliced, 
                                                                ksl=ksl_sliced))
        return seq

    def _make_slices_solenoid(element, num_slices, ksi_sliced):
        thin_positions = element.teapot_slicing(num_slices)
        rad_length = element.length/num_slices
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(xe.ThinSolenoid(f'{element.name}_{idx}', position=thin_pos, 
                                                            ksi=ksi_sliced, 
                                                            rad_length=rad_length))
        return seq

    if isinstance(element, xe.SectorBend):
        if num_slices == 1:
            seq = [xe.ThinMultipole(element.name, position=getattr(element, 'position', 0), knl=[element.angle])]
        if method == 'teapot' and num_slices > 1:
            knl_sliced = [element.angle/num_slices]
            seq = _make_slices_multipoles(element, num_slices, knl_sliced=knl_sliced)
        
        h = element.angle/element.length
        seq.insert(0, xe.DipoleEdge(f'{element.name}_edge_entrance', side='entrance', h=h, e1=element.e1, position=element.start))
        seq.append(xe.DipoleEdge(f'{element.name}_edge_exit', h=h, side='exit', e1=element.e2, position=element.end))
        return seq
        
    if isinstance(element, xe.Multipole):
        if num_slices == 1:
            return [xe.ThinMultipole(element.name, position=getattr(element, 'position', 0), knl=element.knl, ksl=element.ksl)]
        elif method == 'teapot' and num_slices > 1:
            knl_sliced = element.knl/num_slices
            ksl_sliced = element.ksl/num_slices
            return _make_slices_multipoles(element, num_slices, knl_sliced=knl_sliced, ksl_sliced=ksl_sliced)
                
    if isinstance(element, xe.Solenoid):
        if num_slices == 1:
            return [xe.ThinSolenoid(element.name, position=getattr(element, 'position', 0), ksi=element.ksi)]
        elif method == 'teapot' and num_slices > 1:
            delta, distance = element.teapot_slicing(num_slices)
            ksi_sliced = element.ksi/num_slices
            return _make_slices_solenoid(element, num_slices, ksi_sliced)
