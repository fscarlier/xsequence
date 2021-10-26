"""
Module fsf.base_elements
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element classes element property dataclasses for particle accelerator elements.
"""

import math
import fsf.elements_dataclasses as xed
import fsf.elements_functions as xef
from fsf.conversion_utils import conv_utils, cpymad_conv_new, pyat_conv_new, xline_conv


class BaseElement():
    """Class containing base element properties and methods"""
    def __init__(self, name: str, **kwargs):
        self.name = name
        if kwargs is None:
            kwargs = {'temp':0}
        self.id_data = kwargs.pop('id_data', conv_utils.get_id_data(**kwargs))
        self.position_data = kwargs.pop('position_data', conv_utils.get_position_data(**kwargs)) 
        self.aperture_data = kwargs.pop('aperture_data', None)
        self.pyat_data = kwargs.pop('pyat_data', None)
        
    def get_repr_attributes(self):
        repr_attributes = []
        data_attribute_list = ['id_data', 'position_data', 'aperture_data',
                               'strength_data', 'solenoid_data', 'bend_data',
                               'rf_data']

        for key in data_attribute_list:
            try:
                att =  getattr(self, key)
                if att is not None:
                    repr_attributes.append(key)
            except: AttributeError
        return repr_attributes
        
    @property
    def length(self):
        return self.position_data.length
    
    @length.setter
    def length(self, length: float):
        self.position_data.length = length
    
    @classmethod
    def from_cpymad(cls, cpymad_element):
        """ Create Xsequence Element instance from cpymad element """
        return cpymad_conv_new.from_cpymad(cls, cpymad_element)

    def to_cpymad(self, madx):
        """ Create cpymad element in madx instance from Element """
        return cpymad_conv_new.to_cpymad(self, madx)

    @classmethod
    def from_pyat(cls, pyat_element):
        """ Create Xsequence Element instance from pyAT element """
        return pyat_conv_new.from_pyat(cls, pyat_element)

    def to_pyat(self):
        """ Create pyAT element instance from element """
        return pyat_conv_new.to_pyat(self)

    def to_xline(self):
        """ Create Xline element instance from element """
        return xline_conv.convert_element_to_xline(self)

    def _get_slice_positions(self, num_slices=1):
        return xef.get_teapot_slicing_positions(self.position_data, num_slices)
    
    def _get_sliced_element(self, num_slices=1, thin_class=None, **kwargs):
        thin_positions, rad_length = self._get_slice_positions(num_slices=num_slices)
        seq = []
        for idx, thin_pos in enumerate(thin_positions):
            seq.append(thin_class(f'{self.name}_{idx}', radiation_length=rad_length, location=thin_pos, **kwargs) )
        return seq

    def get_dict(self):
        attr_dict = {}
        for k in self.get_repr_attributes():
            attr_dict.update(dict(getattr(self,k)))
        return attr_dict

    def __eq__(self, other):
        compare_list = ['name'] + self.get_repr_attributes()
        for k in compare_list:
            if getattr(self, k) != getattr(other, k):
                return False
        return True

    def __repr__(self) -> str:
        content = ''.join([f', {x}={getattr(self, x)}' for x in self.get_repr_attributes()])
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
        assert self.length >= 0.0, f"Drift {name} has zero or negative length"


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
        
        self.bend_data = kwargs.pop('bend_data', conv_utils.get_bend_data(**kwargs)) 

    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_bend_strength(self.bend_data, num_slices)

    def _get_DipoleEdge(self, side):
        assert side in ['start', 'end']
        h = self.bend_data.angle/self.length
        if side == 'start':
            return DipoleEdge(f'{self.name}_edge_{side}', side=side, h=h, e1=self.bend_data.e1, location=self.position_data.start)
        elif side == 'end':
            return DipoleEdge(f'{self.name}_edge_{side}', side=side, h=h, e1=self.bend_data.e2, location=self.position_data.end)

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


class RectangularBend(SectorBend):   
    """ Rbend element class """
    def __init__(self, name: str, **kwargs):
        self._chord_length = kwargs.pop('length', 0)
        self._rbend_e1 = kwargs.pop('e1', 0)
        self._rbend_e2 = kwargs.pop('e2', 0)
        kwargs['length'] = self._calc_length(kwargs['angle'], self._chord_length)
        kwargs['e1'] = self._rbend_e1+abs(kwargs['angle'])/2.
        kwargs['e2'] = self._rbend_e2+abs(kwargs['angle'])/2.
        
        super().__init__(name, **kwargs)
        
        self.bend_data = kwargs.pop('bend_data', conv_utils.get_bend_data(**kwargs))

    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_bend_strength(self.bend_data, num_slices)


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

    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_solenoid_strength(self.solenoid_data, num_slices)

    def slice_element(self, num_slices=1):
        solenoid_data = self._get_sliced_strength(num_slices=num_slices)
        return self._get_sliced_element(num_slices=num_slices, thin_class=ThinSolenoid, solenoid_data=solenoid_data) 
    
    @property
    def ks(self):
        return self.strength_data.ks
    
    @ks.setter
    def ks(self, ks: float):
        self.strength_data.ks = ks

    @property
    def ksi(self):
        return self.strength_data.ks*self.length
    
    @ksi.setter
    def ksi(self, ksi: float):
        self.strength_data.ks = ksi/self.length


class Multipole(BaseElement):
    """ Multipole element class """
    def __init__(self, name: str, strength_class=xed.MultipoleStrengthData, **kwargs):
        super().__init__(name, **kwargs)
        self.strength_data = kwargs.pop('strength_data', conv_utils.get_strength_data(strength_class=strength_class, **kwargs))
        
    def _get_sliced_strength(self, num_slices=1):
        return xef.get_sliced_multipole_strength(self.strength_data, num_slices)

    def slice_element(self, num_slices=1):
        strength_data = self._get_sliced_strength(num_slices=num_slices)
        return self._get_sliced_element(num_slices=num_slices, thin_class=ThinMultipole, strength_data=strength_data) 

    @property
    def knl(self):
        return self.strength_data.kn*self.length
    
    @knl.setter
    def knl(self, knl):
        self.strength_data.kn = knl/self.length


class Quadrupole(Multipole):
    """ Quadrupole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.QuadrupoleData, **kwargs)

    @property
    def k1(self):
        return self.strength_data.k1
    
    @k1.setter
    def k1(self, k1: float):
        self.strength_data.k1 = k1

    @property
    def k1s(self):
        return self.strength_data.k1s
    
    @k1s.setter
    def k1s(self, k1s: float):
        self.strength_data.k1s = k1s


class Sextupole(Multipole):
    """ Sextupole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.SextupoleData, **kwargs)

    @property
    def k2(self):
        return self.strength_data.k2
    
    @k2.setter
    def k1(self, k2: float):
        self.strength_data.k2 = k2

    @property
    def k2s(self):
        return self.strength_data.k2s
    
    @k2s.setter
    def k2s(self, k2s: float):
        self.strength_data.k2s = k2s


class Octupole(Multipole):
    """ Octupole element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, strength_class=xed.OctupoleData, **kwargs)

    @property
    def k3(self):
        return self.strength_data.k3
    
    @k3.setter
    def k3(self, k3: float):
        self.strength_data.k3 = k3

    @property
    def k3s(self):
        return self.strength_data.k3s
    
    @k3s.setter
    def k3s(self, k3s: float):
        self.strength_data.k3s = k3s


class RFCavity(BaseElement):
    """ RFCavity element class """
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.rf_data = kwargs.pop('rf_data', conv_utils.get_rf_data(**kwargs))
        

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
        self.solenoid_data = kwargs.pop('solenoid_data', conv_utils.get_solenoid_data(**kwargs))
        self.radiation_length = kwargs.pop('radiation_length', 0)
        assert self.length == 0

    @property
    def ksi(self):
        return self.strength_data.ks*self.length
    
    @ksi.setter
    def ksi(self, ksi: float):
        self.strength_data.ks = ksi/self.length


class ThinRFMultipole(RFCavity):
    def __init__(self, name: str, **kwargs):
        super().__init__(name, **kwargs)
        self.radiation_length = kwargs.pop('radiation_length', 0)
        assert self.length == 0


CPYMAD_TO_FSF_MAP = {'marker': Marker, 
                     'drift':  Drift, 
                     'rbend':  RectangularBend, 
                     'sbend':  SectorBend, 
                     'quadrupole': Quadrupole, 
                     'sextupole': Sextupole, 
                     'collimator': Collimator, 
                     'rfcavity': RFCavity}


PYAT_TO_FSF_MAP = {'Marker': Marker, 
                   'Drift':  Drift, 
                   'Dipole':  SectorBend, 
                   'Quadrupole': Quadrupole, 
                   'Sextupole': Sextupole, 
                   'Collimator': Collimator, 
                   'RFCavity': RFCavity}
                
