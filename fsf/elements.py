"""
Module fsf.base_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element classes element property dataclasses for particle accelerator elements.
"""

import math
import fsf.elements_dataclasses as xed
import fsf.elements_functions as xef

class BaseElement():
    """Class containing base element properties and methods"""
    def __init__(self, name: str, **kwargs):
        self.repr_attributes = ['id_data', 'position_data', 'aperture_data']

        self.name = name
        if kwargs is None:
            kwargs = {'temp':0}
        self.id_data = kwargs.pop('id_data', 
                                xed.ElementID(**{k:kwargs[k] for k in xed.ElementID.INIT_PROPERTIES if k in kwargs}))
        self.position_data = kwargs.pop('position_data', 
                                xed.ElementPosition(**{k:kwargs[k] for k in xed.ElementPosition.INIT_PROPERTIES if k in kwargs}))
        self.aperture_data = kwargs.pop('aperture_data', 
                                xed.Aperture())

    @property
    def length(self):
        return self.position.length
    
    @length.setter
    def length(self, length: float):
        self.position.length = length

    def _get_slice_positions(self, num_slices=1):
        return xef.get_teapot_slicing_positions(self.position, num_slices)
    
    def _get_sliced_element(self, num_slices=1, thin_class=None, **kwargs):
        thin_positions, rad_length = self._get_slice_positions(num_slices=num_slices)
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(thin_class(f'{self.name}_{idx}', radiation_length=rad_length, distance=thin_pos, **kwargs) )
        return seq

    def __eq__(self, other):
        compare_list = ['name'] + self.repr_attributes
        for k in compare_list:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.repr_attributes])
        return f'{self.__class__.__name__}(' + f'{self.name}' + content + ')'


class ThinBaseElement(BaseElement):
    """ Thin base element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        assert self.length == 0.0, f"ThinBaseElement {name} has non-zero length"



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
        super().__init__(name, **kwargs)
        
        self.bend_data = kwargs.pop('bend_data', 
                            xed.BendData(**{k:kwargs[k] for k in xed.BendData.INIT_PROPERTIES if k in kwargs})
                         )
        self.repr_attributes.append('bend_data')

    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_bend_strength(self.bend, num_slices)

    def _get_DipoleEdge(self, side):
        assert side in ['start', 'end']
        h = self.angle/self.length
        return DipoleEdge(f'{self.name}_edge_{side}', side=side, h=h, e1=self.e1, position=self.start)

    def slice_element(self, num_slices=1):
        strength_data = self._get_sliced_strength(num_slices=num_slices)
        sliced_bend =  self._get_sliced_element(num_slices=num_slices, thin_class=ThinSolenoid, strength_data=strength_data) 
        sliced_bend.insert(0, self._get_DipoleEdge('start'))
        sliced_bend.append(self._get_DipoleEdge('end'))
        return sliced_bend


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
        
        self.bend_data = kwargs.pop('bend_data', 
                            xed.BendData(**{k:kwargs[k] for k in xed.BendData.INIT_PROPERTIES if k in kwargs})
                         )
        self.repr_attributes.append('bend_data')

    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_bend_strength(self.bend, num_slices)


class DipoleEdge(BaseElement):
    """ Dipole edge element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=DipoleEdge, **kwargs)


class Solenoid(BaseElement):
    """ Solenoid element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.solenoid_data = kwargs.pop('solenoid_data', 
                                xed.SolenoidData(**{k:kwargs[k] for k in xed.SolenoidData.INIT_PROPERTIES if k in kwargs})
                             )
        self.repr_attributes.append('solenoid_data')

    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_solenoid_strength(self.solenoid_strength, num_slices)

    def slice_element(self, num_slices=1):
        solenoid_data = self._get_sliced_strength(num_slices=num_slices)
        return self._get_sliced_element(num_slices=num_slices, thin_class=ThinSolenoid, solenoid_data=solenoid_data) 
    
    @property
    def ks(self):
        return self.strength.ks
    
    @ks.setter
    def ks(self, ks: float):
        self.strength.ks = ks

    @property
    def ksi(self):
        return self.strength.ks*self.length
    
    @ksi.setter
    def ksi(self, ksi: float):
        self.strength.ks = ksi/self.length


class Multipole(BaseElement):
    """ Multipole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)

        self.strength_data = kwargs.pop('strength_data', 
                                xed.MultipoleStrengthData(**{k:kwargs[k] for k in xed.MultipoleStrengthData.INIT_PROPERTIES if k in kwargs})
                             )
        self.repr_attributes.append('strength_data')
        
    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_multipole_strength(self.strength, num_slices)

    def slice_element(self, num_slices=1):
        strength_data = self._get_sliced_strength(num_slices=num_slices)
        return self._get_sliced_element(num_slices=num_slices, thin_class=ThinMultipole, strength_data=strength_data) 

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
        super().__init__(name, **kwargs)
        
        self.rf_data = kwargs.pop('rf_data', 
                            xed.RFCavityData(**{k:kwargs[k] for k in xed.RFCavityData.INIT_PROPERTIES if k in kwargs})
                       )
        self.repr_attributes.append('rf_data')
        


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
        self.radiation_length = kwargs.pop('radiation_length', 0)
        assert self.length == 0


class ThinSolenoid(BaseElement):
    """ ThinSolenoid element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        
        self.solenoid_data = kwargs.pop('solenoid_data', 
                                xed.ThinSolenoidData(**{k:kwargs[k] for k in xed.ThinSolenoidData.INIT_PROPERTIES if k in kwargs})
                             )
        self.repr_attributes.append('solenoid_data')
        
        self.radiation_length = kwargs.pop('radiation_length', 0)
        assert self.length == 0

    @property
    def ksi(self):
        return self.strength.ks*self.length
    
    @ksi.setter
    def ksi(self, ksi: float):
        self.strength.ks = ksi/self.length


class ThinRFMultipole(RFCavity):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.radiation_length = kwargs.pop('radiation_length', 0)
        assert self.length == 0

