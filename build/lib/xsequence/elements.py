"""
Module xsequence.base_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element classes element property dataclasses for particle accelerator elements.
"""

import math
import numpy as np
from abc import ABC, abstractmethod

import xsequence.elements_dataclasses as xed
import xsequence.helpers.elements_functions as xef

from xsequence.conversion_utils import conv_utils
from xsequence.conversion_utils.cpymad import cpymad_conv
from xsequence.conversion_utils.pyat import pyat_conv
from xsequence.conversion_utils.xline import xline_conv


class ShouldUseMultipoleError(Exception):
    """Exception raised for trying to define kn/ks for Quadrupole, Sextupole, Octupole."""
    def __init__(self, name: str, attr: str):
        self.name = name
        self.attr = attr
        self.message = f'Cannot define {attr} for element {name} -> Should use Multipole class instead'
        super().__init__(self.message)


class BaseElement():
    """Class containing base element properties and methods"""
    
    length = xef._property_factory('position_data', 'length', docstring='Get and set length attribute')
    position = xef._property_factory('position_data', 'position', docstring='Get and set position attribute')
    
    def __init__(self, name: str, **kwargs):
        self.name = name
        if kwargs is None:
            kwargs = {'empty_kw_dict':None}
        self.id_data = kwargs.pop('id_data', conv_utils.get_id_data(**kwargs))
        self.parameter_data = kwargs.pop('parameter_data', conv_utils.get_parameter_data(**kwargs))
        self.position_data = kwargs.pop('position_data', conv_utils.get_position_data(**kwargs)) 
        self.aperture_data = kwargs.pop('aperture_data', None)
        self.pyat_data = kwargs.pop('pyat_data', None)
    
    def _set_as_dict(self, key, value):
        if key == xed.ElementID.INIT_PROPERTIES:
            setattr(self.id_data, key, value)
        elif key == xed.ElementParameterData.INIT_PROPERTIES:
            setattr(self.parameter_data, key, value)
        elif key == xed.ElementPosition.INIT_PROPERTIES:
            setattr(self.position_data, key, value)
        elif key == xed.ApertureData.INIT_PROPERTIES:
            setattr(self.aperture_data, key, value)
        elif key == xed.PyatData.INIT_PROPERTIES:
            setattr(self.pyat_data, key, value)
        else:
            setattr(self, key, value)

    @classmethod
    def from_cpymad(cls, cpymad_element):
        """ Create Xsequence Element instance from cpymad element """
        return cpymad_conv.from_cpymad(cls, cpymad_element)

    def to_cpymad(self, madx):
        """ Create cpymad element in madx instance from Element """
        return cpymad_conv.to_cpymad(self, madx)

    @classmethod
    def from_pyat(cls, pyat_element):
        """ Create Xsequence Element instance from pyAT element """
        return pyat_conv.from_pyat(cls, pyat_element)

    def to_pyat(self):
        """ Create pyAT element instance from element """
        return pyat_conv.to_pyat(self)

    def to_xline(self):
        """ Create Xline element instance from element """
        return xline_conv.convert_element_to_xline(self)

    def _get_slice_positions(self, num_slices=1):
        """ Create Xline element instance from element """
        return xef.get_teapot_slicing_positions(self.position_data, num_slices)
    
    def _get_sliced_element(self, num_slices=1, thin_class=None, **kwargs):
        thin_positions, rad_length = self._get_slice_positions(num_slices=num_slices)
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(thin_class(f'{self.name}_{idx}', radiation_length=rad_length, location=thin_pos, **kwargs) )
        return seq

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

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.__dict__ if x != 'name'])
        return f'{self.__class__.__name__}({self.name}{content})'


class ThickElement(ABC):
    """ Thick element class """
    @abstractmethod
    def slice_element(self):
        pass


class ThinElement:
    """ Thin element class """
    def __init__(self, name: str, **kwargs):
        assert self.length == 0.0, f"BaseElement, ThinElement {name} has non-zero length"


class Marker(BaseElement, ThinElement):
    """ Marker element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
    

class Drift(BaseElement):
    """ Drift element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length >= 0.0, f"Drift {name} has zero or negative length"


class Collimator(Drift):
    """ Collimator element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class Monitor(Drift):
    """ Monitor element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class Placeholder(Drift):
    """ Placeholder element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class Instrument(Drift):
    """ Instrument element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class SectorBend(BaseElement):
    """ Sector bend element class """
    def __init__(self, name: str, **kwargs):
        self.angle = kwargs.pop('angle', 0.0)
        self.e1 = kwargs.pop('e1', 0.0)
        self.e2 = kwargs.pop('e2', 0.0)
        self.k0 = kwargs.pop('k0', 0.0)
        super().__init__(name, **kwargs)

    def _get_DipoleEdge(self, side):
        h = self.angle/self.length
        if side == 'entrance':
            return DipoleEdge(f'{self.name}_edge_{side}', 
                                side=side, h=h, edge_angle=self.e1, 
                                location=self.position_data.start)
        elif side == 'exit':
            return DipoleEdge(f'{self.name}_edge_{side}', 
                                side=side, h=h, edge_angle=self.e2, 
                                location=self.position_data.end)

    def slice_element(self, num_slices=1):
        knl = [self.angle / num_slices]
        sliced_bend =  self._get_sliced_element(num_slices=num_slices, thin_class=ThinMultipole, knl=knl) 
        sliced_bend.insert(0, self._get_DipoleEdge('entrance'))
        sliced_bend.append(self._get_DipoleEdge('exit'))
        return sliced_bend

    def _calc_chordlength(self, angle: float, length: float) :
        return length*(2*math.sin(angle/2.))/angle


class RectangularBend(SectorBend):   
    """ Rectangular bend element class """
    def __init__(self, name: str, **kwargs):
        self._chord_length = kwargs.pop('length', 0)
        self._rbend_e1 = kwargs.pop('e1', 0)
        self._rbend_e2 = kwargs.pop('e2', 0)
        kwargs['length'] = self._calc_arclength(kwargs['angle'], self._chord_length)
        kwargs['e1'] = self._rbend_e1+abs(kwargs['angle'])/2.
        kwargs['e2'] = self._rbend_e2+abs(kwargs['angle'])/2.
        super().__init__(name, **kwargs)

    def _calc_arclength(self, angle: float, chord_length: float):
        return (angle*chord_length)/(2*math.sin(angle/2.))


class DipoleEdge(BaseElement):
    """ Dipole edge element class """
    def __init__(self, name: str, **kwargs):
        self.h = kwargs.pop('h', 0.0) 
        self.edge_angle = kwargs.pop('edge_angle', 0.0)
        self.side = kwargs.pop('side', 'entrance')
        assert self.side in ['entrance', 'exit']
        super().__init__(name, **kwargs)


class Solenoid(BaseElement):
    """ Solenoid element class """
    def __init__(self, name: str, **kwargs):
        self.ks = kwargs.pop('ks', 0.0)
        super().__init__(name, **kwargs)
        
    @property
    def ksi(self):
        return self.ks*self.length

    @ksi.setter
    def ksi(self, ksi: float):
        self.ks = ksi/self.length
    
    def _get_sliced_strength(self, num_slices=1):
        return self.ksi/num_slices

    def slice_element(self, num_slices=1):
        ksi_sliced = self._get_sliced_strength(num_slices=num_slices)
        return self._get_sliced_element(num_slices=num_slices, thin_class=ThinSolenoid, ksi=ksi_sliced) 
    

class _BaseMultipole(ABC):
    """ Multipole element class """
    def slice_element(self, num_slices=1):
        knl_sliced = self.knl / num_slices
        ksl_sliced = self.ksl / num_slices
        return self._get_sliced_element(num_slices=num_slices, thin_class=ThinMultipole, knl=knl_sliced, ksl=ksl_sliced) 
    
    @property
    @abstractmethod
    def kn(self):
        pass 
    
    @property
    @abstractmethod
    def ks(self):
        pass 
    
    @kn.setter
    @abstractmethod
    def kn(self):
        pass 
    
    @ks.setter
    @abstractmethod
    def ks(self):
        pass 
    
    @property
    def knl(self):
        return self.kn*self.length
    
    @property
    def ksl(self):
        return self.kn*self.length
    
    @knl.setter
    def knl(self, knl):
        self.kn = knl / self.length
    
    @ksl.setter
    def ksl(self, ksl):
        self.kn = ksl / self.length


class Multipole(BaseElement, _BaseMultipole):
    """ Multipole element class """
    def __init__(self, name: str, **kwargs):
        self.kn = kwargs.pop('kn', np.zeros(2))
        self.ks = kwargs.pop('ks', np.zeros(2))
        super().__init__(name, **kwargs)
        
    @property
    def kn(self):
        return self._kn 

    @kn.setter
    def kn(self, kn):
        self._kn = kn 

    @property
    def ks(self):
        return self._ks 
    
    @ks.setter
    def ks(self, ks):
        self._ks = ks 
    
    def _update_arrays(self, min_order: int = 1):
        kn = np.trim_zeros(self.kn, trim='b')
        ks = np.trim_zeros(self.ks, trim='b')
        if len(kn) == 0: kn = np.zeros(1)
        if len(ks) == 0: ks = np.zeros(1)
        self.order = max(len(kn), len(ks), min_order)
        self.kn = np.pad(kn, (0, self.order-len(kn)))
        self.ks = np.pad(ks, (0, self.order-len(ks)))


class Quadrupole(BaseElement, _BaseMultipole):
    """ Quadrupole element class """
    def __init__(self, name: str, **kwargs):
        self.k1 = kwargs.pop('k1', 0.0)
        self.k1s = kwargs.pop('k1s', 0.0)
        super().__init__(name, **kwargs)

    @property
    def kn(self):
        return np.array([0.0, self.k1]) 

    @property
    def ks(self):
        return np.array([0.0, self.k1s]) 
    
    @kn.setter
    def kn(self, kn):
        raise ShouldUseMultipoleError(self.name, 'kn') 

    @ks.setter
    def ks(self, ks):
        raise ShouldUseMultipoleError(self.name, 'ks') 



class Sextupole(BaseElement, _BaseMultipole):
    """ Sextupole element class """
    def __init__(self, name: str, **kwargs):
        self.k2 = kwargs.pop('k2', 0.0)
        self.k2s = kwargs.pop('k2s', 0.0)
        super().__init__(name, **kwargs)
    
    @property
    def kn(self):
        return np.array([0.0, 0.0, self.k2]) 

    @property
    def ks(self):
        return np.array([0.0, 0.0, self.k2s]) 
    
    @kn.setter
    def kn(self, kn):
        raise ShouldUseMultipoleError(self.name, 'kn') 

    @ks.setter
    def ks(self, ks):
        raise ShouldUseMultipoleError(self.name, 'ks') 


class Octupole(BaseElement, _BaseMultipole):
    """ Octupole element class """
    def __init__(self, name: str, **kwargs):
        self.k3 = kwargs.pop('k3', 0.0)
        self.k3s = kwargs.pop('k3s', 0.0)
        super().__init__(name, **kwargs)

    @property
    def kn(self):
        return np.array([0.0, 0.0, 0.0, self.k3]) 

    @property
    def ks(self):
        return np.array([0.0, 0.0, 0.0, self.k3s]) 
    
    @kn.setter
    def kn(self, kn):
        raise ShouldUseMultipoleError(self.name, 'kn') 

    @ks.setter
    def ks(self, ks):
        raise ShouldUseMultipoleError(self.name, 'ks') 


class RFCavity(BaseElement):
    """ RFCavity element class """
    def __init__(self, name: str, **kwargs):
        self.voltage = kwargs.pop('voltage', 0.0)
        self.frequency = kwargs.pop('frequency', 0.0)
        self.lag = kwargs.pop('lag', 0.0)
        self.energy = kwargs.pop('energy', 0.0)
        self.harmonic_number = kwargs.pop('harmonic_number', 0.0)
        super().__init__(name, **kwargs)


class HKicker(BaseElement):
    """ Horizontal kicker element class """
    def __init__(self, name: str, **kwargs):
        self.kick = kwargs.pop('kick', 0.0)
        super().__init__(name, **kwargs)


class VKicker(BaseElement):
    """ Vertical kicker element class """
    def __init__(self, name: str, **kwargs):
        self.kick = kwargs.pop('kick', 0.0)
        super().__init__(name, **kwargs)


class TKicker(BaseElement):
    """ TKicker element class """
    def __init__(self, name: str, **kwargs):
        self.vkick = kwargs.pop('vkick', 0.0)
        self.hkick = kwargs.pop('hkick', 0.0)
        super().__init__(name, **kwargs)


class ThinMultipole(BaseElement, ThinElement):
    """ Thin multipole element class """
    def __init__(self, name: str, **kwargs):
        self.knl = kwargs.pop('knl', np.zeros(2))
        self.ksl = kwargs.pop('ksl', np.zeros(2))
        super().__init__(name, **kwargs)


class ThinSolenoid(BaseElement, ThinElement):
    """ ThinSolenoid element class """
    def __init__(self, name: str, **kwargs):
        self.ksi = kwargs.pop('ksi', 0.0)
        super().__init__(name, **kwargs)

    @property
    def ks(self):
        return self.ksi/self.position_data.radiation_length
    
    @ks.setter
    def ks(self, ks: float):
        self.ksi = ks * self.position_data.radiation_length


class ThinRFMultipole(BaseElement, ThinElement):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


CPYMAD_TO_FSF_MAP = { 
                    'marker'          : Marker         ,  
                    'drift'           : Drift          ,  
                    'collimator'      : Collimator     ,  
                    'monitor'         : Monitor        ,  
                    'placeholder'     : Placeholder    ,  
                    'instrument'      : Instrument     ,  
                    'sbend'           : SectorBend     ,  
                    'rbend'           : RectangularBend,     
                    'dipedge'         : DipoleEdge     ,  
                    'solenoid'        : Solenoid       ,  
                    'multipole'       : ThinMultipole      ,  
                    'quadrupole'      : Quadrupole     ,  
                    'sextupole'       : Sextupole      ,  
                    'octupole'        : Octupole       ,  
                    'rfcavity'        : RFCavity       ,  
                    'hkicker'         : HKicker        ,  
                    'vkicker'         : VKicker        ,  
                    'tkicker'         : TKicker        ,  
                    'thinmultipole'   : ThinMultipole  ,  
                    'thinsolenoid'    : ThinSolenoid   ,  
                    'thinrfmultipole' : ThinRFMultipole, 
                    }


PYAT_TO_FSF_MAP = {'Marker': Marker, 
                   'Drift':  Drift, 
                   'Dipole':  SectorBend, 
                   'Quadrupole': Quadrupole, 
                   'Sextupole': Sextupole, 
                   'Collimator': Collimator, 
                   'RFCavity': RFCavity}


def convert_arbitrary_cpymad_element(cpymad_element):
    return CPYMAD_TO_FSF_MAP[cpymad_element.base_type.name].from_cpymad(cpymad_element)


def convert_arbitrary_pyat_element(pyat_element):
    return PYAT_TO_FSF_MAP[pyat_element.__class__.__name__].from_pyat(pyat_element)


