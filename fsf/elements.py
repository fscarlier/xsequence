"""
Module fsf.elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element classes for accelerator sequence definitions.
"""

import copy, at
import numpy as np
import fsf.lattice 
from  conversion_utils import pyat_conv, cpymad_conv


class Element:
    """
    Base element class  
    """

    def __init__(self, name, **kwargs):
        """
        Args:
            name : string
                name of element
        
        Key Args:
            length: float
                length of element [m]
        """
        self.name = name
        self.length = kwargs.pop('length', 0.0)
        self.position = kwargs.pop('position', 0.0)
        self.parent = kwargs.pop('parent', self.__class__.__name__)
        self.update(**kwargs)


    def __eq__(self, other):
        return self.__dict__ == other.__dict__


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
        return self.pos['centre']


    @property
    def start(self):
        return self.pos['start']


    @property
    def end(self):
        return self.pos['end']


    @position.setter
    def position(self, position, loc='centre'):
        self.pos = {'centre':position, 
                    'start':position - self.length/2.,
                    'end':position + self.length/2.}

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


    @property
    def int_steps(self):
        return self._int_steps 


    @int_steps.setter
    def int_steps(self, int_steps):
        self._int_steps = int_steps 


    def teapot_slicing(self, num_slices):
        delta = self.length*(1/(2*num_slices + 2))
        distance = self.length*(num_slices/(num_slices**2 - 1))
        return delta, distance 


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

    def slice_element(self, **kwargs):
        return [self]


class DipEdge(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.h = kwargs.pop('h', 0)
        self.e1 = kwargs.pop('e1', 0)
        self.side = kwargs.pop('side', 'entrance')
        assert self.side in ('entrance', 'exit'), f"Invalid side Attribute for {self.name} DipEdge"


class Sbend(Element):   
    """
    Sbend element class
    """
    def __init__(self, name, **kwargs):
        """
        Args:
            name : string
                name of element
        
        Key Args:
            length: float
                arclength of element [m]
        """
        self.e1 = kwargs.pop('e1', 0)
        self.e2 = kwargs.pop('e2', 0)
        super().__init__(name, **kwargs)
        self.chord_length = kwargs.pop('chord_length', self._calc_chordlength())

    
    def _calc_arclength(self) :
        """
        Calculate arclength from angle and chordlength
        
        Returns:
            Float with arclength
        """
        return (self.angle*self.chord_length)/(2*np.sin(self.angle/2.))


    def _calc_chordlength(self) :
        """
        Calculate chordlength from angle and arclength
        
        Returns:
            Float with chordlength 
        """
        return self.length*(2*np.sin(self.angle/2.))/self.angle


    def convert_to_rbend(self):
        """
        Convert Sbend element to Rbend element
        
        Returns:
            Rbend instance of element 
        """
        kwargs = copy.copy(vars(self))
        kwargs['arc_length'] = kwargs.pop('length')
        kwargs['length'] = kwargs.pop('chord_length')
        if 'e1' in kwargs:
            kwargs['e1'] = kwargs.pop('e1')-self.angle/2.
        if 'e2' in kwargs:
            kwargs['e2'] = kwargs.pop('e2')-self.angle/2.
        kwargs.pop('name')
        return Rbend(self.name, **kwargs) 
    
    def slice_element(self, num_slices=1, method='teapot', output='list'):
        try: num_slices = self.int_steps
        except: AttributeError

        if self.length == 0:
            return [self]

        if num_slices == 1:
            h = self.angle/self.length
            start = getattr(self, 'position', 0) - self.length/2.            
            end = getattr(self, 'position', 0) + self.length/2.            
            seq = [ThinMultipole(self.name, position=getattr(self, 'position', 0), knl=[self.angle])]
            seq.insert(0, DipEdge(f'{self.name}_edge_entrance', side='entrance', h=h, e1=self.e1, position=start))
            seq.append(DipEdge(f'{self.name}_edge_exit', h=h, side='exit', e1=self.e2, position=end))
            return seq
        if method == 'teapot' and num_slices > 1:
            delta, distance = self.teapot_slicing(num_slices)
            angle_sliced = self.angle/num_slices
            h = self.angle/self.length
            seq = []
            seq.append(ThinMultipole(f'{self.name}_0', position=self.start+delta, knl=[angle_sliced]))
            for i in range(num_slices-1):
                seq.append(ThinMultipole(f'{self.name}_{i+1}', position=seq[-1].position + distance, knl=[angle_sliced]))
            
            seq.insert(0, DipEdge(f'{self.name}_edge_entrance', side='entrance', h=h, e1=self.e1, position=self.start))
            seq.append(DipEdge(f'{self.name}_edge_exit', h=h, side='exit', e1=self.e2, position=self.end))

            if output == 'lattice': 
                seq.insert(0, Marker(f'{self.name}_start', position=self.start))
                seq.append(Marker(f'{self.name}_start', position=self.end))
                sequence = fsf.lattice.Lattice(self.name, seq, key='sequence') 
            else:
                sequence = seq
            return sequence 


class Rbend(Element):   
    """
    Rbend element class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)
        self.arc_length = kwargs.pop('arc_length', self._calc_arclength())
        assert np.isclose(self.length, self._calc_chordlength(), rtol=1e-8)

     
    def _calc_arclength(self) :
        """
        Calculate arclength from angle and chordlength
        
        Returns:
            Float with arclength
        """
        return (self.angle*self.length)/(2*np.sin(self.angle/2.))


    def _calc_chordlength(self) :
        """
        Calculate chordlength from angle and arclength
        
        Returns:
            Float with chordlength 
        """
        return self.arc_length*(2*np.sin(self.angle/2.))/self.angle


    def convert_to_sbend(self):
        """
        Convert Rbend element to Sbend element
        
        Returns:
            Sbend instance of element 
        """
        kwargs = copy.copy(vars(self))
        kwargs['chord_length'] = kwargs.pop('length')
        kwargs['length'] = kwargs.pop('arc_length')
        if 'e1' in kwargs:
            kwargs['e1'] = kwargs.pop('e1')+abs(self.angle)/2.
        if 'e2' in kwargs:
            kwargs['e2'] = kwargs.pop('e2')+abs(self.angle)/2.
        kwargs.pop('name')
        return Sbend(self.name, **kwargs) 

    
    def slice_element(self, num_slices=1, method='teapot', output='list'):
        sbend = self.convert_to_sbend()
        return sbend.slice_element(num_slices=num_slices, method='teapot', output='list')


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


    def slice_element(self, num_slices=1, method='teapot', output='list'):
        try: num_slices = self.int_steps
        except: AttributeError

        if self.length == 0:
            return [self]

        if num_slices == 1:
            return [ThinMultipole(self.name, position=getattr(self, 'position', 0), knl=self.knl, ksl=self.ksl)]
        elif method == 'teapot' and num_slices > 1:
            delta, distance = self.teapot_slicing(num_slices)
            knl_sliced = self.knl/num_slices
            ksl_sliced = self.ksl/num_slices
            seq = []
            seq.append(ThinMultipole(f'{self.name}_0', position=self.start+delta, knl=knl_sliced, ksl=ksl_sliced))
            for i in range(num_slices-1):
                seq.append(ThinMultipole(f'{self.name}_{i+1}', position=seq[-1].position + distance, knl=knl_sliced, ksl=ksl_sliced))

            if output == 'lattice': 
                seq.insert(0, Marker(f'{self.name}_start', position=self.start))
                seq.append(Marker(f'{self.name}_start', position=self.end))
                sequence = fsf.lattice.Lattice(self.name, seq, key='sequence') 
            else:
                sequence = seq
            return sequence 


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

    @property
    def k2s(self):
        return self.ks[2]
    
    @k2s.setter
    def k2s(self, ks):
        self.ks[2] = ks


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

    @property
    def k3s(self):
        return self.ks[3]
    
    @k3s.setter
    def k3s(self, ks):
        self.ks[3] = ks


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


class ThinQuadrupole(ThinMultipole):
    """
    Thin Quadrupole class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinSextupole(ThinMultipole):
    """
    Thin Sextupole class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ThinOctupole(ThinMultipole):
    """
    Thin Octupole class
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class RFCavity(Element):
    """
    RFCavity element class
    """
    def __init__(self, name, **kwargs):
        self.volt = kwargs.pop('volt', 0.0)
        self.freq = kwargs.pop('freq', 0.0)
        self.lag = kwargs.pop('lag', 0.0)
        super().__init__(name, **kwargs)

    def slice_element(self):
        if self.length == 0:
            return [self]


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
        super().__init__(name, **kwargs)

    
class BeamBeam(Element):
    """
    Beam-beam element class
    
    charge : int
        charge of particles in the opposite beam
    sigx : float
        horizontal beam size of opposite beam
    sigy : float
        vertical beam size of opposite beam
    dx : float
        horizontal orbit offset of opposite beam
    dy : float
        vertical orbit offset of opposite beam
    shape : str
        radial density shape of the opposite beam, default='gaussian'
    """
    def __init__(self, name, **kwargs):
        self.charge = kwargs.pop('charge', 1)
        self.sigx = kwargs.pop('sigx', 1)
        self.sigy = kwargs.pop('sigy', 1)
        self.dx = kwargs.pop('dx', 0)
        self.dy = kwargs.pop('dy', 0)
        self.shape = kwargs.pop('shape', 'gaussian')
        super().__init__(name, **kwargs)


class DipoleEdge(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ClosedOrbitCorrector(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TransverseKicker(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class TravellingWaveCavity(Element):
    """
    """
    def __init__(self, name, **kwargs):
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


class ElectrostaticSeparator(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class BeamPositionMonitor(Element):
    """
    """
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Instrument(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class Placeholder(Element):
    def __init__(self, name, **kwargs):
        super().__init__(name, **kwargs)


class ArbitraryMatrixElement(Element):
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
                
