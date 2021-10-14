"""
Module fsf.elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element classes for accelerator sequence definitions.
"""

import copy, math
import numpy as np
from  conversion_utils import xline_conv, pyat_conv, cpymad_conv

class BaseElement:
    """
    Base element class  
    """
    def __init__(self, name, **kwargs):
        """
        Args:
            name : string, name of element
        Key Args:
            length: float, length of element [m]
        """
        self.name = name
        self.length = kwargs.pop('length', 0.0)
        self.set_position(kwargs.pop('position', 0.0), reference=kwargs.pop('reference', None))
        self.parent = kwargs.pop('parent', self.__class__.__name__)
        self.update(**kwargs)

    def update(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def items(self):
        """Iterates through the data members including slots and properties"""
        # Get attributes
        for k, v in vars(self).items():
            yield k, v

    @property
    def position(self):
        return self._position['centre']

    @property
    def start(self):
        return self._position['start']

    @property
    def end(self):
        return self._position['end']

    @position.setter
    def position(self, position):
        self.set_position(position)

    def set_position(self, position, reference=None):
        pos = position
        if reference:
            self._relative_position = position
            if isinstance(reference, (float, int)):
                self.reference = reference 
                pos = self._relative_position + self.reference
            elif isinstance(reference, Element):
                self.reference = reference.position 
                pos = self._relative_position + self.reference
        self._position = {'centre':pos, 
                          'start':pos - self.length/2.,
                          'end':pos + self.length/2.}

    @classmethod
    def from_cpymad(cls, cpymad_element):
        """ 
        Create specific Element instance from cpymad element
        """
        return cpymad_conv.convert_element_from_cpymad(cls, cpymad_element)

    def to_cpymad(self, madx):
        """ 
        Create cpymad element in madx instance from Element
        """
        return cpymad_conv.convert_element_to_cpymad(self, madx)

    @classmethod
    def from_pyat(cls, pyat_element):
        """ 
        Create specific Element instance from pyAT element
        """
        return pyat_conv.convert_element_from_pyat(cls, pyat_element)

    def to_pyat(self):
        """ 
        Create pyAT Element instance from element
        """
        return pyat_conv.convert_element_to_pyat(self)

    def to_xline(self):
        """ 
        Create pyAT Element instance from element
        """
        return xline_conv.convert_element_to_xline(self)

    def __str__(self):
        args_dict = vars(self).items()
        args_str = [f'{k}={v}' for k,v in args_dict if k!= 'name']
        return f"{self.__class__.__name__}('{self.name}', {', '.join(args_str)})"

    def __repr__(self):
        args_dict = vars(self).items()
        args_str = [f'{k}={v}' for k,v in args_dict if k!= 'name']
        return f"{self.__class__.__name__}('{self.name}', {', '.join(args_str)})"

    def __eq__(self, second_element):
        """Return equality of two dicts including numpy arrays"""
        first = dict(self.items())
        second = dict(second_element.items())
        
        if first.keys() != second.keys():
            return False
        
        for key in first:
            if type(first[key]).__module__ == np.__name__:
                if len(first[key]) != len(second[key]):
                    return False
                arr_eq = np.isclose(first[key], second[key])
                if False in arr_eq:
                    return False
            else:
                if first[key] != second[key]:
                    return False
        return True


class Element(BaseElement):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    @property
    def int_steps(self):
        return self._int_steps 

    @int_steps.setter
    def int_steps(self, int_steps):
        self._int_steps = int_steps 

    def teapot_slicing(self, num_slices):
        delta = self.length*(1/(2*num_slices + 2))
        distance = self.length*(num_slices/(num_slices**2 - 1))
        thin_positions =  [self.start+delta]
        for i in range(num_slices-1):
            thin_positions.append(thin_positions[-1] + distance)
        return thin_positions 

    def slice_element(self, num_slices=1, method='teapot'):
        try: num_slices = self.int_steps
        except: AttributeError

        if self.length == 0:
            return [self]

        def _make_slices_multipoles(self, num_slices, knl_sliced=[0], ksl_sliced=[0]):
            thin_positions = self.teapot_slicing(num_slices)
            rad_length = self.length/num_slices
            seq = []
            for idx, thin_pos in enumerate(thin_positions):
                seq.append(ThinMultipole(f'{self.name}_{idx}', position=thin_pos, 
                                                                 rad_length=rad_length, 
                                                                 knl=knl_sliced, 
                                                                 ksl=ksl_sliced))
            return seq

        def _make_slices_solenoid(self, num_slices, ksi_sliced):
            thin_positions = self.teapot_slicing(num_slices)
            rad_length = self.length/num_slices
            seq = []
            for idx, thin_pos in enumerate(thin_positions):
                seq.append(ThinSolenoid(f'{self.name}_{idx}', position=thin_pos, 
                                                              ksi=ksi_sliced, 
                                                              rad_length=rad_length))
            return seq

        if isinstance(self, Sbend):
            if num_slices == 1:
                seq = [ThinMultipole(self.name, position=getattr(self, 'position', 0), knl=[self.angle])]
            if method == 'teapot' and num_slices > 1:
                knl_sliced = [self.angle/num_slices]
                seq = _make_slices_multipoles(self, num_slices, knl_sliced=knl_sliced)
            
            h = self.angle/self.length
            seq.insert(0, DipoleEdge(f'{self.name}_edge_entrance', side='entrance', h=h, e1=self.e1, position=self.start))
            seq.append(DipoleEdge(f'{self.name}_edge_exit', h=h, side='exit', e1=self.e2, position=self.end))
            return seq
            
        if isinstance(self, Multipole):
            if num_slices == 1:
                return [ThinMultipole(self.name, position=getattr(self, 'position', 0), knl=self.knl, ksl=self.ksl)]
            elif method == 'teapot' and num_slices > 1:
                knl_sliced = self.knl/num_slices
                ksl_sliced = self.ksl/num_slices
                return _make_slices_multipoles(self, num_slices, knl_sliced=knl_sliced, ksl_sliced=ksl_sliced)
                 
        if isinstance(self, Solenoid):
            if num_slices == 1:
                return [ThinSolenoid(self.name, position=getattr(self, 'position', 0), ksi=self.ksi)]
            elif method == 'teapot' and num_slices > 1:
                delta, distance = self.teapot_slicing(num_slices)
                ksi_sliced = self.ksi/num_slices
                return _make_slices_solenoid(self, num_slices, ksi_sliced)


class Drift(Element):
    """
    Drift element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length >= 0.0, f"Drift {name} has negative length"


class Marker(Element):
    """
    Marker element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length == 0.0, f"Marker {name} has non-zero length"


class DipoleEdge(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.h = kwargs.pop('h', 0)
        self.e1 = kwargs.pop('e1', 0)
        self.side = kwargs.pop('side', 'entrance')
        assert self.side in ('entrance', 'exit'), f"Invalid side Attribute for {self.name} DipoleEdge"


class Sbend(Element):   
    """
    Sbend element class
    """
    def __init__(self, name, **kwargs):
        """
        Key Args:
            angle: float, bending angle of element
            length: float, arclength of element [m]
        """
        self.angle = kwargs.pop('angle')
        self.e1 = kwargs.pop('e1', 0)
        self.e2 = kwargs.pop('e2', 0)
        super().__init__(name, **kwargs)
    
    def _calc_length(self, angle, chord_length):
        return (angle*chord_length)/(2*math.sin(angle/2.))

    def _calc_chordlength(self, angle, length) :
        return length*(2*math.sin(angle/2.))/angle


class Rbend(Sbend):   
    """
    Rbend element class
    """
    def __init__(self, name, **kwargs):
        self._chord_length = kwargs.pop('length', 0)
        self._rbend_e1 = kwargs.pop('e1', 0)
        self._rbend_e2 = kwargs.pop('e2', 0)
        kwargs['length'] = self._calc_length(kwargs['angle'], self._chord_length)
        kwargs['e1'] = self._rbend_e1+abs(kwargs['angle'])/2.
        kwargs['e2'] = self._rbend_e2+abs(kwargs['angle'])/2.
        super().__init__(name, **kwargs)
        assert np.isclose(self._chord_length, self._calc_chordlength(self.angle, self.length), atol=1e-14)


class Multipole(Element):
    """
    Multipole element class
    """
    def __init__(self, name, **kwargs):
        """
        Setting multipole strengths. knl and ksl have precedence over k1, k2, k3
        """
        self.length = kwargs['length']
        assert self.length != 0, "Thick {} ({}) defined with length 0. Use Thin{} instead"\
                                 .format(self.__class__.__name__, name, self.__class__.__name__)
        self.kn = np.array(kwargs.pop('kn', [kwargs.pop('k0', 0.0), kwargs.pop('k1', 0.0), 
                                             kwargs.pop('k2', 0.0), kwargs.pop('k3', 0.0)]))
        self.ks = np.array(kwargs.pop('ks', [kwargs.pop('k0s', 0.0), kwargs.pop('k1s', 0.0), 
                                             kwargs.pop('k2s', 0.0), kwargs.pop('k3s', 0.0)]))
        
        self.kn = np.trim_zeros(self.kn, trim='b')
        self.ks = np.trim_zeros(self.ks, trim='b')
        if len(self.kn) == 0: self.kn = np.zeros(1)
        if len(self.ks) == 0: self.ks = np.zeros(1)
        self.order = max(len(self.kn), len(self.ks))
        self.kn = np.pad(self.kn, (0, self.order-len(self.kn)))
        self.ks = np.pad(self.ks, (0, self.order-len(self.ks)))
        
        self.knl = np.array(kwargs.pop('knl', self.kn*self.length)) 
        self.ksl = np.array(kwargs.pop('ksl', self.ks*self.length))
        super().__init__(name, **kwargs)


class Quadrupole(Multipole):
    """
    Quadrupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)

    @property
    def k1(self):
        return self.kn[1]
    
    @k1.setter
    def k1(self, k):
        self.kn[1] = k
        self.knl = self.kn*self.length

    @property
    def k1s(self):
        return self.ks[1]
    
    @k1s.setter
    def k1s(self, ks):
        self.ks[1] = ks
        self.ksl = self.ks*self.length


class Sextupole(Multipole):
    """
    Sextupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    @property
    def k2(self):
        return self.kn[2]
    
    @k2.setter
    def k2(self, k):
        self.kn[2] = k
        self.knl = self.kn*self.length

    @property
    def k2s(self):
        return self.ks[2]
    
    @k2s.setter
    def k2s(self, ks):
        self.ks[2] = ks
        self.ksl = self.ks*self.length


class Octupole(Multipole):
    """
    Octupole element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
    
    @property
    def k3(self):
        return self.kn[3]
    
    @k3.setter
    def k3(self, k):
        self.kn[3] = k
        self.knl = self.kn*self.length

    @property
    def k3s(self):
        return self.ks[3]
    
    @k3s.setter
    def k3s(self, ks):
        self.ks[3] = ks
        self.ksl = self.ks*self.length


class ThinMultipole(Element):
    """
    Multipole element class
    """
    def __init__(self, name, **kwargs):
        self.knl = np.array(kwargs.pop('knl', [0.0]))
        self.ksl = np.array(kwargs.pop('ksl', [0.0]))
        self.knl = np.trim_zeros(self.knl, trim='b')
        self.ksl = np.trim_zeros(self.ksl, trim='b')
        self.order = max(len(self.knl), len(self.ksl))
        self.knl = np.pad(self.knl, (0, self.order-len(self.knl)))
        self.ksl = np.pad(self.ksl, (0, self.order-len(self.ksl)))
        
        super().__init__(name, **kwargs)
        assert self.length == 0, "Thin{} ({}) defined with length > 0. Use {} instead"\
                                 .format(self.__class__.__name__, name, self.__class__.__name__)


class RFCavity(Element):
    """
    RFCavity element class
    """
    def __init__(self, name, **kwargs):
        self.volt = kwargs.pop('volt', 0.0)
        self.freq = kwargs.pop('freq', 0.0)
        self.lag = kwargs.pop('lag', 0.0)
        super().__init__(name, **kwargs)


class Collimator(Drift):
    """
    Collimator element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Solenoid(Element):
    """
    Solenoid element class
    """
    def __init__(self, name, **kwargs):
        self.ks = kwargs.pop('ks', 0.0)
        super().__init__(name, **kwargs)
        self.ksi = self.ks*self.length


class ThinSolenoid(Element):
    """
    ThinSolenoid element class
    """
    def __init__(self, name, **kwargs):
        self.ksi = kwargs.pop('ksi', 0.0)
        self.ks = kwargs.pop('ks', 0.0)
        super().__init__(name, **kwargs)

    
class BeamBeam(Element):
    """
    Beam-beam element class
    
    charge : int, charge of particles in the opposite beam
    sigx : float, horizontal beam size of opposite beam
    sigy : float, vertical beam size of opposite beam
    dx : float, horizontal orbit offset of opposite beam
    dy : float, vertical orbit offset of opposite beam
    shape : str, radial density shape of the opposite beam, default='gaussian'
    """
    def __init__(self, name, **kwargs):
        self.charge = kwargs.pop('charge', 1)
        self.sigx = kwargs.pop('sigx', 1)
        self.sigy = kwargs.pop('sigy', 1)
        self.dx = kwargs.pop('dx', 0)
        self.dy = kwargs.pop('dy', 0)
        self.shape = kwargs.pop('shape', 'gaussian')
        super().__init__(name, **kwargs)


class ThinRFMultipole(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class CrabCavity(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ACDipole(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamPositionMonitor(Marker):
    """
    BPM base class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


CPYMAD_TO_FSF_MAP = {'marker': Marker, 
                     'drift':  Drift, 
                     'rbend':  Rbend, 
                     'sbend':  Sbend, 
                     'quadrupole': Quadrupole, 
                     'sextupole': Sextupole, 
                     'collimator': Collimator, 
                     'rfcavity': RFCavity}


PYAT_TO_FSF_MAP = {'Marker': Marker, 
                   'Drift':  Drift, 
                   'Dipole':  Sbend, 
                   'Quadrupole': Quadrupole, 
                   'Sextupole': Sextupole, 
                   'Collimator': Collimator, 
                   'RFCavity': RFCavity}
                
