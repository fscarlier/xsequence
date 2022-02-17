from node import Node
import xsequence.elements as xe

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


def get_sliced_element(node: Node, elements, thin_class, **kwargs):
    element = elements[node.element_name]
    thin_positions = get_slice_positions(element)
    thin_nodes_list = []
    thin_elements_dict = {}
    for idx, thin_pos in enumerate(thin_positions):
        thin_name = f'{node.element_name}_sliced_{idx}'
        thin_nodes_list.append(Node(thin_name, reference=node.position, location=thin_pos, length=0.0))
        thin_elements_dict[thin_name] = xe.ThinMultipole(thin_name, radiation_length=element.length/element.num_slices, **kwargs)
    return thin_nodes_list, thin_elements_dict


def slice_bend(node: Node, element):
    rad_length = element.length/element.num_slices
    
    if isinstance(element, xe.SectorBend):
        knl = [element.angle / element.num_slices]
        thin_element = xe.ThinMultipole(radiation_length=rad_length, knl=knl)
    if isinstance(element, xe.Solenoid):
        ksi_sliced = self.ksi / self.num_slices
        thin_element = xe.ThinSolenoid(radiation_length=rad_length, ksi=ksi_sliced) 

    sliced_bend_nodes, thin_elements_dict = get_sliced_element(node, thin_class=xe.ThinMultipole, knl=knl) 
    
    h = element.angle/element.length
    bend_entrance = xe.DipoleEdge(f'{self.name}_edge_entrance', 
                            side='entrance', h=h, edge_angle=element.e1)
    bend_exit = xe.DipoleEdge(f'{self.name}_edge_exit', 
                            side='exit', h=h, edge_angle=element.e2)
    
    sliced_bend.insert(0, bend_entrance)
    sliced_bend.append(bend_exit)
    
    return thin_nodes_list, thin_elements_dict


def slice_solenoid(self):
    ksi_sliced = self.ksi / self.num_slices
    return self._get_sliced_element(thin_class=ThinSolenoid, ksi=ksi_sliced) 


def slice_base_multipole(self):
    knl_sliced = self.knl / self.num_slices
    ksl_sliced = self.ksl / self.num_slices
    return self._get_sliced_element(thin_class=ThinMultipole, knl=knl_sliced, ksl=ksl_sliced) 


def slice_hkicker(self):
    kick_sliced = self.kick / self.num_slices
    return self._get_sliced_element(method='uniform', 
                                    thin_class=HKicker, kick=kick_sliced) 


def slice_vkicker(self):
    kick_sliced = self.kick / self.num_slices
    return self._get_sliced_element(method='uniform', 
                                    thin_class=VKicker, kick=kick_sliced) 


def slice_tkicker(self):
    hkick_sliced = self.hkick / self.num_slices
    vkick_sliced = self.vkick / self.num_slices
    return self._get_sliced_element(method='uniform', 
                                    thin_class=TKicker, hkick=hkick_sliced, vkick=vkick_sliced) 


ThickElement: ThinElement
Marker      : Marker
Drift       : Drift
Collimator  : Drift
Monitor     : Drift
Placeholder : Drift
Instrument  : Drift

SectorBend
RectangularBend   
DipoleEdge


Solenoid    : ThinSolenoid


_BaseMultipole

Multipole
Quadrupole
Sextupole
Octupole


RFCavity


HKicker


VKicker


TKicker


ThinMultipole




ThinRFMultipole

