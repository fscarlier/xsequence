"""
Module fsf.base_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element classes element property dataclasses for particle accelerator elements.
"""

import math
import fsf.elements_dataclasses as xed

class BaseElement():
    """Class containing base element properties and methods"""
    def __init__(self, name: str, bend_class=None, strength_class=None, rf_class=None, **kwargs):
        self.repr_attributes = ['element_id', 'position', 'aperture']

        self.name = name
        if kwargs is None:
            kwargs = {'temp':0}
        self.element_id = xed.ElementID(**{k:kwargs[k] for k in xed.ElementID.INIT_PROPERTIES if k in kwargs})
        self.position = xed.ElementPosition(**{k:kwargs[k] for k in xed.ElementPosition.INIT_PROPERTIES if k in kwargs})
        self.aperture = xed.Aperture()

        if bend_class:
            self.bend = bend_class(**{k:kwargs[k] for k in bend_class.INIT_PROPERTIES if k in kwargs})
            self.repr_attributes.append('bend')
        if strength_class:
            self.strength = strength_class(**{k:kwargs[k] for k in strength_class.INIT_PROPERTIES if k in kwargs})
            self.repr_attributes.append('strength')
        if rf_class:
            self.rf_params = rf_class(**{k:kwargs[k] for k in rf_class.INIT_PROPERTIES if k in kwargs})
            self.repr_attributes.append('rf_params')

    @property
    def length(self):
        return self.position.length
    
    @length.setter
    def length(self, length: float):
        self.position.length = length

    def __eq__(self, other):
        compare_list = ['name'] + self.repr_attributes
        for k in compare_list:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.repr_attributes])
        return f'{self.__class__.__name__}(' + f'{self.name}' + content + ')'


class Marker(BaseElement):
    """ Marker element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length == 0.0, f"Marker {name} has non-zero length"
    

class Drift(BaseElement):
    """ Drift element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length > 0.0, f"Drift {name} has zero or negative length"


class Collimator(Drift):
    """ Collimator element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class Monitor(Drift):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class Placeholder(Drift):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class Instrument(Drift):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class SectorBend(BaseElement):
    """ Sbend element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, bend_class=xed.BendData, **kwargs)

    def _calc_length(self, angle: float, chord_length: float):
        return (angle*chord_length)/(2*math.sin(angle/2.))

    def _calc_chordlength(self, angle: float, length: float) :
        return length*(2*math.sin(angle/2.))/angle


class Rectangularbend(BaseElement):   
    """ Rbend element class """
    def __init__(self, name: str, **kwargs):
        self._chord_length = kwargs.pop('length', 0)
        self._rbend_e1 = kwargs.pop('e1', 0)
        self._rbend_e2 = kwargs.pop('e2', 0)
        kwargs['length'] = self._calc_length(kwargs['angle'], self._chord_length)
        kwargs['e1'] = self._rbend_e1+abs(kwargs['angle'])/2.
        kwargs['e2'] = self._rbend_e2+abs(kwargs['angle'])/2.
        
        super().__init__(name, bend_class=xed.BendData, **kwargs)


class DipoleEdge(BaseElement):
    """ Dipole edge element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=DipoleEdge, **kwargs)


class Solenoid(BaseElement):
    """ Solenoid element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.SolenoidData, **kwargs)

    @property
    def ks(self):
        return self.strength.ks
    
    @ks.setter
    def ks(self, ks: float):
        self.strength.ks = ks

    @property
    def ksi(self):
        return self.strength.ks*self.length
    
    @ks.setter
    def ks(self, ksi: float):
        self.strength.ks = ksi/self.length


class Multipole(BaseElement):
    """ Multipole element class """
    def __init__(self, name: str, strength_class=xed.MultipoleStrengthData, **kwargs):
        super().__init__(name, strength_class=strength_class, **kwargs)

    @property
    def knl(self):
        return self.strength.kn*self.length
    
    @knl.setter
    def knl(self, knl):
        self.strength.kn = knl/self.length


class Quadrupole(Multipole):
    """ Quadrupole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.QuadrupoleData, **kwargs)

    @property
    def k1(self):
        return self.strength.k1
    
    @k1.setter
    def k1(self, k1: float):
        self.strength.k1 = k1

    @property
    def k1s(self):
        return self.strength.k1s
    
    @k1s.setter
    def k1s(self, k1s: float):
        self.strength.k1s = k1s


class Sextupole(Multipole):
    """ Sextupole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.SextupoleData, **kwargs)

    @property
    def k2(self):
        return self.strength.k2
    
    @k2.setter
    def k1(self, k2: float):
        self.strength.k2 = k2

    @property
    def k2s(self):
        return self.strength.k2s
    
    @k2s.setter
    def k2s(self, k2s: float):
        self.strength.k2s = k2s


class Octupole(Multipole):
    """ Octupole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.OctupoleData, **kwargs)

    @property
    def k3(self):
        return self.strength.k3
    
    @k3.setter
    def k3(self, k3: float):
        self.strength.k3 = k3

    @property
    def k3s(self):
        return self.strength.k3s
    
    @k3s.setter
    def k3s(self, k3s: float):
        self.strength.k3s = k3s


class RFCavity(BaseElement):
    """ RFCavity element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, rf_class=xed.RFCavityData, **kwargs)


class HKicker(BaseElement):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class VKicker(BaseElement):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class TKicker(BaseElement):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)


class ThinMultipole(BaseElement):
    """ Thin multipole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.ThinMultipoleStrengthData, **kwargs)
        self.length_radiation = kwargs.pop('length_radiation', 0)
        assert self.length == 0


class ThinSolenoid(Solenoid):
    """ ThinSolenoid element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.length_radiation = kwargs.pop('length_radiation', 0)
        assert self.length == 0


class ThinRFMultipole(RFCavity):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.length_radiation = kwargs.pop('length_radiation', 0)
        assert self.length == 0

