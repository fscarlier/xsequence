"""
Module xsequence.base_elements
------------------
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
    def __init__(self,
                 name: str,
                 length: float=0.0,
                 num_slices: int=1,
                 **kwargs):
        self.name = name
        self.length = length
        self.num_slices = num_slices

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
        for key in self.__dict__:
            if isinstance(getattr(self, key), xed.BaseElementData):
                attr_dict.update(dict(getattr(self,key)))
            else:
                attr_dict[key] = getattr(self, key)
        return attr_dict

    def __eq__(self, other):
        if self.__class__.__name__ != other.__class__.__name__:
            return False
        for key in self.__dict__:
            if key in ['kn', 'ks', 'knl', 'ksl']:
                array_1 = np.trim_zeros(getattr(self, key), trim='b')
                array_2 = np.trim_zeros(getattr(other, key), trim='b')
                if len(array_1) != len(array_2):
                    return False
                arr_eq = np.isclose(array_1, array_2, rtol=1e-8)
                if False in arr_eq:
                    return False
            else:
                if getattr(self, key) != getattr(other, key):
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
    REQUIREMENTS = ['']

    def __init__(self, name: str, **kwargs):
        self._thin_type = Marker
        super().__init__(name, **kwargs)


class Drift(BaseElement):
    """ Drift element class """
    REQUIREMENTS = ['length']

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
    REQUIREMENTS = ['angle', 'e1', 'e2']

    def __init__(self, name: str, **kwargs):
        self.angle = kwargs.pop('angle', 0.0)
        self.e1 = kwargs.pop('e1', 0.0)
        self.e2 = kwargs.pop('e2', 0.0)
        self.k0 = kwargs.pop('k0', 0.0)
        self.k1 = kwargs.pop('k1', 0.0)
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
    REQUIREMENTS = ['edge_angle', 'h', 'side']

    def __init__(self, name: str, **kwargs):
        self.h = kwargs.pop('h', 0.0)
        self.edge_angle = kwargs.pop('edge_angle', 0.0)
        self.side = kwargs.pop('side', 'entrance')
        assert self.side in ['entrance', 'exit']
        super().__init__(name, **kwargs)


class Solenoid(BaseElement):
    """ Solenoid element class """
    REQUIREMENTS = ['ks']

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


class Multipole(BaseElement):
    """ Multipole element class """
    REQUIREMENTS = ['length', 'knl', 'ksl']

    def __init__(self,
                 name: str,
                 knl: np.ndarray=np.zeros(20),
                 ksl: np.ndarray=np.zeros(20),
                 **kwargs):
        self.knl = knl
        self.ksl = ksl
        super().__init__(name, **kwargs)

    @property
    def kn(self):
        return self.knl/self.length

    @property
    def ks(self):
        return self.ksl/self.length

    @kn.setter
    def kn(self, kn):
        self.knl = kn * self.length

    @ks.setter
    def ks(self, ks):
        self.ksl = ks * self.length

    def _get_thin_element(self):
        knl_sliced = self.knl / self.num_slices
        ksl_sliced = self.ksl / self.num_slices
        return ThinMultipole(self.name, radiation_length=self.length/self.num_slices, knl=knl_sliced, ksl=ksl_sliced)


class Quadrupole(BaseElement):
    """ Quadrupole element class """
    REQUIREMENTS = ['length', 'k1', 'k1s']

    def __init__(self, name: str, **kwargs):
        self.k1  = kwargs.pop('k1', 0.0)
        self.k1s = kwargs.pop('k1s', 0.0)
        super().__init__(name, **kwargs)

    @property
    def kn(self):
        return np.array([0.0, self.k1])

    @property
    def ks(self):
        return np.array([0.0, self.k1s])

    @property
    def knl(self):
        return self.kn*self.length

    @property
    def ksl(self):
        return self.ks*self.length

    def _get_thin_element(self):
        knl_sliced = self.knl / self.num_slices
        ksl_sliced = self.ksl / self.num_slices
        return ThinMultipole(self.name, radiation_length=self.length/self.num_slices, knl=knl_sliced, ksl=ksl_sliced)


class Sextupole(BaseElement):
    """ Sextupole element class """
    REQUIREMENTS = ['length', 'k2', 'k2s']

    def __init__(self, name: str, **kwargs):
        self.k2  = kwargs.pop('k2', 0.0)
        self.k2s = kwargs.pop('k2s', 0.0)
        super().__init__(name, **kwargs)

    @property
    def kn(self):
        return np.array([0.0, 0.0, self.k2])

    @property
    def ks(self):
        return np.array([0.0, 0.0, self.k2s])

    @property
    def knl(self):
        return self.kn*self.length

    @property
    def ksl(self):
        return self.ks*self.length

    def _get_thin_element(self):
        knl_sliced = self.knl / self.num_slices
        ksl_sliced = self.ksl / self.num_slices
        return ThinMultipole(self.name, radiation_length=self.length/self.num_slices, knl=knl_sliced, ksl=ksl_sliced)


class Octupole(BaseElement):
    REQUIREMENTS = ['length', 'k3', 'k3s']

    """ Octupole element class """
    def __init__(self, name: str, **kwargs):
        self.k3  = kwargs.pop('k3', 0.0)
        self.k3s = kwargs.pop('k3s', 0.0)
        super().__init__(name, **kwargs)

    @property
    def kn(self):
        return np.array([0.0, 0.0, 0.0, self.k3])

    @property
    def ks(self):
        return np.array([0.0, 0.0, 0.0, self.k3s])

    @property
    def knl(self):
        return self.kn*self.length

    @property
    def ksl(self):
        return self.ks*self.length

    def _get_thin_element(self):
        knl_sliced = self.knl / self.num_slices
        ksl_sliced = self.ksl / self.num_slices
        return ThinMultipole(self.name, radiation_length=self.length/self.num_slices, knl=knl_sliced, ksl=ksl_sliced)


class RFCavity(BaseElement):
    """ RFCavity element class """
    REQUIREMENTS = ['length', 'voltage', 'frequency', 'lag']

    def __init__(self,
                 name: str,
                 voltage: float,
                 frequency: float,
                 lag: float,
                 **kwargs):
        self.voltage = voltage
        self.frequency = frequency
        self.lag = lag
        self.energy = kwargs.pop('energy', 0.0)
        self.harmonic_number = kwargs.pop('harmonic_number', 0.0)
        super().__init__(name, **kwargs)


class HKicker(BaseElement):
    """ Horizontal kicker element class """
    REQUIREMENTS = ['length', 'kick']

    def __init__(self, name: str, **kwargs):
        self.kick = kwargs.pop('kick', 0.0)
        super().__init__(name, **kwargs)

    def _get_thin_element(self):
        kick_sliced = self.kick / self.num_slices
        return HKicker(self.name, radiation_length=self.length/self.num_slices, kick=kick_sliced)


class VKicker(BaseElement):
    """ Vertical kicker element class """
    REQUIREMENTS = ['length', 'kick']

    def __init__(self, name: str, **kwargs):
        self.kick = kwargs.pop('kick', 0.0)
        super().__init__(name, **kwargs)

    def _get_thin_element(self):
        kick_sliced = self.kick / self.num_slices
        return VKicker(self.name, radiation_length=self.length/self.num_slices, kick=kick_sliced)


class TKicker(BaseElement):
    """ TKicker element class """
    REQUIREMENTS = ['length', 'hkick', 'vkick']

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
    REQUIREMENTS = ['knl', 'ksl']

    def __init__(self, name: str, **kwargs):
        self.knl = kwargs.pop('knl', np.zeros(4))
        self.ksl = kwargs.pop('ksl', np.zeros(4))
        super().__init__(name, **kwargs)


class ThinSolenoid(ThinElement):
    """ ThinSolenoid element class """
    REQUIREMENTS = ['ksi']

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
