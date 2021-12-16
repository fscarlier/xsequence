from abc import ABC, abstractmethod
from xsequence.lattice import Lattice
from xsequence.elements import BaseElement

from xsequence.xconverters.bmad import bmad_conv, bmad_lattice_conv
from xsequence.xconverters.cpymad import cpymad_conv, cpymad_lattice_conv
from xsequence.xconverters.pyat import pyat_conv, pyat_lattice_conv
from xsequence.xconverters.xtrack import xtrack_conv, xtrack_lattice_conv
from xsequence.xconverters.sad import sad_conv, sad_lattice_conv
from xsequence.xconverters.elegant import elegant_conv, elegant_lattice_conv


class Converter(ABC):

    def __init__(self) -> None:
        pass
    
    @abstractmethod
    def import_model(self) -> Lattice:
        pass
    
    @abstractmethod
    def export_model(self):
        pass

    @abstractmethod
    def import_element(self) -> BaseElement:
        pass
    
    @abstractmethod
    def export_element(self):
        pass


class BmadConverter(Converter):
    """Converter class for conversions between Bmad and Xsequence"""
    def import_model(self):
        pass
    
    def export_model(self, lattice: Lattice) -> str:
        return bmad_lattice_conv.to_bmad(lattice)

    def import_element(self):
        pass
    
    def export_element(self, element: BaseElement) -> str:
        return bmad_conv.to_bmad_str(element)


class CpymadConverter(Converter):
    """Converter class for conversions between Bmad and Xsequence"""
    def import_model(self):
        return cpymad_lattice_conv.from_cpymad(lattice)
    
    def export_model(self, lattice: Lattice) -> str:
        return cpymad_lattice_conv.to_cpymad(lattice)

    def import_element(self, cpymad_element):
        return cpymad_conv.from_cpymad(cpymad_element)
    
    def export_element(self, element: BaseElement) -> str:
        return cpymad_conv.to_cpymad(element)



class PyatConverter(Converter):
    """Converter class for conversions between Bmad and Xsequence"""
    def import_model(self):
        pass
    
    def export_model(self, lattice: Lattice) -> str:
        return pyat_lattice_conv.to_pyat(lattice)

    def import_element(self):
        pass
    
    def export_element(self, element: BaseElement) -> str:
        return pyat_conv.to_pyat(element)



class SadConverter(Converter):
    """Converter class for conversions between Bmad and Xsequence"""
    def import_model(self):
        return sad_lattice_conv.from_sad(lattice)
    
    def export_model(self, lattice: Lattice) -> str:
        pass

    def import_element(self):
        return sad_conv.from_sad(element)
    
    def export_element(self, element: BaseElement) -> str:
        pass



class ElegantConverter(Converter):
    """Converter class for conversions between Bmad and Xsequence"""
    def import_model(self):
        pass
    
    def export_model(self, lattice: Lattice) -> str:
        return elegant_lattice_conv.to_elegant(lattice)

    def import_element(self):
        pass
    
    def export_element(self, element: BaseElement) -> str:
        return elegant_conv.to_elegant(element)



class XtrackConverter(Converter):
    """Converter class for conversions between Bmad and Xsequence"""
    def import_model(self):
        pass
    
    def export_model(self, lattice: Lattice) -> str:
        return xtrack_lattice_conv.to_xtrack(lattice)

    def import_element(self):
        pass
    
    def export_element(self, element: BaseElement) -> str:
        return xtrack_conv.to_xtrack(element)




