"""
Module xsequence.base_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element classes element property dataclasses for particle accelerator elements.
"""

import math
import numpy as np
import xsequence.elements_dataclasses as xed


def add_unequal_arrays(a, b):
    if len(a) == len(b):
        return a + b
    elif len(a) < len(b):
        a = a.copy()
        a.resize(b.shape)
        return a + b
    else:
        b = b.copy()
        b.resize(a.shape)
        return b + a


class ShouldUseMultipoleError(Exception):
    """Exception raised for trying to define kn/ks for Quadrupole, Sextupole, Octupole."""
    def __init__(self, name: str, attr: str):
        self.message = f'Cannot define {attr} of element {name} -> Should use Multipole class instead'
        super().__init__(name, self.message)


class BaseElement:
    """Class containing base element properties and methods"""
    def __init__(self, name: str, **kwargs):
        self.name = name
        self.length = kwargs.pop('length', 0.0)
        self.num_slices = kwargs.pop('num_slices', 1)
        
        if kwargs is None:
            kwargs = {'empty_kw_dict':None}
        self.aperture_data = kwargs.pop('aperture_data', None)
        self.pyat_data = kwargs.pop('pyat_data', None)

    def _set_from_key(self, key, value):
        if key in xed.ApertureData.INIT_PROPERTIES:
            setattr(self.aperture_data, key, value)
        elif key in xed.PyatData.INIT_PROPERTIES:
            setattr(self.pyat_data, key, value)
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

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.__dict__ if x != 'name'])
        return f'{self.__class__.__name__}({self.name}{content})'


class ThinElement(BaseElement):
    """ Thin element class """
    def __init__(self, name: str, **kwargs):
        self.radiation_length = kwargs.pop('radiation_length', 0.0)
        super().__init__(name, **kwargs)
        assert self.length == 0.0, f"BaseElement, ThinElement has non-zero length"


class Marker(ThinElement):
    """ Marker element class """
    def __init__(self, name: str, **kwargs):
        self._thin_type = Marker
        super().__init__(name, **kwargs)
    

class Drift(BaseElement):
    """ Drift element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length >= 0.0, f"Drift has zero or negative length"


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

    def _get_thin_element(self):
        knl = [self.angle / self.num_slices]
        return ThinMultipole(self.name, radiation_length=self.length/self.num_slices, knl=knl)

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
        if angle == 0:
            return chord_length
        else:
            return (angle*chord_length)/(2*math.sin(angle/2.))


class DipoleEdge(ThinElement):
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
        
    def _get_thin_element(self):
        ksi_sliced = self.ksi / self.num_slices
        return ThinSolenoid(self.name, radiation_length=self.length/self.num_slices, ksi=ksi_sliced) 
    
    @property
    def ksi(self):
        return self.ks*self.length

    @ksi.setter
    def ksi(self, ksi: float):
        self.ks = ksi/self.length
    

class BaseMultipole(BaseElement):
    """ Multipole element class """
    def __init__(self, name: str, magnetic_errors=xed.MultipoleError(), **kwargs):
        super().__init__(name, **kwargs)
        self.magnetic_errors = magnetic_errors
    
    def _update_arrays(self, arr1, arr2, min_order: int = 1):
        arr1 = np.trim_zeros(arr1, trim='b')
        arr2 = np.trim_zeros(arr2, trim='b')
        if len(arr1) == 0: arr1 = np.zeros(1)
        if len(arr2) == 0: arr2 = np.zeros(1)
        order = max(len(arr1), len(arr2), min_order)
        arr1 = np.pad(arr1, (0, order-len(arr1)))
        arr2 = np.pad(arr2, (0, order-len(arr2)))
        return arr1, arr2


class Multipole(BaseElement):
    """ Multipole element class """
    def __init__(self, name: str, **kwargs):
        self.kn = kwargs.pop('kn', np.zeros(20))
        self.ks = kwargs.pop('ks', np.zeros(20))
        super().__init__(name, **kwargs)
    
    @property
    def knl(self):
        return self.kn*self.length
    
    @property
    def ksl(self):
        return self.ks*self.length
    
    @knl.setter
    def knl(self, knl):
        self.kn = knl / self.length
    
    @ksl.setter
    def ksl(self, ksl):
        self.kn = ksl / self.length
    
    def _get_thin_element(self):
        knl_sliced = self.knl / self.num_slices
        ksl_sliced = self.ksl / self.num_slices
        return ThinMultipole(self.name, radiation_length=self.length/self.num_slices, knl=knl_sliced, ksl=ksl_sliced)
    

class Quadrupole(Multipole):
    """ Quadrupole element class """
    def __init__(self, name: str, **kwargs):
        kwargs['kn'] = np.array([0.0, kwargs.pop('k1', 0.0), 0.0, 0.0])
        kwargs['ks'] = np.array([0.0, kwargs.pop('k1s', 0.0), 0.0, 0.0])
        super().__init__(name, **kwargs)

    @property
    def k1(self):
        return self.kn[1]

    @property
    def k1s(self):
        return self.ks[1]
    

class Sextupole(Multipole):
    """ Sextupole element class """
    def __init__(self, name: str, **kwargs):
        kwargs['kn'] = np.array([0.0, 0.0, kwargs.pop('k2', 0.0), 0.0])
        kwargs['ks'] = np.array([0.0, 0.0, kwargs.pop('k2s', 0.0), 0.0])
        super().__init__(name, **kwargs)

    @property
    def k2(self):
        return self.kn[2]

    @property
    def k2s(self):
        return self.ks[2]


class Octupole(Multipole):
    """ Octupole element class """
    def __init__(self, name: str, **kwargs):
        kwargs['kn'] = np.array([0.0, 0.0, 0.0, kwargs.pop('k3', 0.0)])
        kwargs['ks'] = np.array([0.0, 0.0, 0.0, kwargs.pop('k3s', 0.0)])
        super().__init__(name, **kwargs)

    @property
    def k3(self):
        return self.kn[3]

    @property
    def k3s(self):
        return self.ks[3]


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
    
    def _get_thin_element(self):
        kick_sliced = self.kick / self.num_slices
        return HKicker(self.name, radiation_length=self.length/self.num_slices, kick=kick_sliced)


class VKicker(BaseElement):
    """ Vertical kicker element class """
    def __init__(self, name: str, **kwargs):
        self.kick = kwargs.pop('kick', 0.0)
        super().__init__(name, **kwargs)
    
    def _get_thin_element(self):
        kick_sliced = self.kick / self.num_slices
        return VKicker(self.name, radiation_length=self.length/self.num_slices, kick=kick_sliced)
    

class TKicker(BaseElement):
    """ TKicker element class """
    def __init__(self, name: str, **kwargs):
        self.vkick = kwargs.pop('vkick', 0.0)
        self.hkick = kwargs.pop('hkick', 0.0)
        super().__init__(name, **kwargs)
    
    def _get_thin_element(self):
        hkick_sliced = self.hkick / self.num_slices
        vkick_sliced = self.vkick / self.num_slices
        return TKicker(self.name, radiation_length=self.length/self.num_slices, hkick=hkick_sliced, vkick=vkick_sliced)


class ThinMultipole(ThinElement):
    """ Thin multipole element class """
    def __init__(self, name: str, **kwargs):
        self.knl = kwargs.pop('knl', np.zeros(4))
        self.ksl = kwargs.pop('ksl', np.zeros(4))
        super().__init__(name, **kwargs)


class ThinSolenoid(ThinElement):
    """ ThinSolenoid element class """
    def __init__(self, name: str, **kwargs):
        self.ksi = kwargs.pop('ksi', 0.0)
        super().__init__(name, **kwargs)

    @property
    def ks(self):
        return self.ksi/self.radiation_length
    
    @ks.setter
    def ks(self, ks: float):
        self.ksi = ks * self.radiation_length


class ThinRFMultipole(ThinElement):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
