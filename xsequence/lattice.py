"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import scipy
import numpy as np
import xsequence.elements as xe

from xsequence.conversion_utils.cpymad import cpymad_lattice_conv
from xsequence.conversion_utils.pyat import pyat_lattice_conv
from xsequence.conversion_utils.xline import xline_lattice_conv
from xsequence.conversion_utils.sad import sad_lattice_conv

from xsequence.helpers import pyat_functions
from collections import OrderedDict
from xsequence.lattice_baseclasses import Line, Sequence
from typing import List

class Lattice:
    """ A class used to represent an accelerator lattice """
    def __init__(self, name: str, element_list: OrderedDict, key: str = 'line', **kwargs):
        self.name = name
        self.params = {'key':key, 'energy':kwargs.pop('energy', None)}
        
        if self.params['key'] == 'line':
            self.line = Line(element_list)
            self.line._set_positions()
        elif self.params['key'] == 'sequence':
            self.sequence = Sequence(element_list)

        if 'xdeps_manager' in kwargs:
            self.xdeps_manager = kwargs['xdeps_manager']

    def get_total_length(self) -> float:
        return self.line._get_total_length()

    def _update_cavity_energy(self):
        cavities = self.get_class(xe.RFCavity)
        for cav in cavities:
            cav.energy = self.params['energy']

    def _update_harmonic_number(self):
        cavities = self.get_class(xe.RFCavity)
        for cav in cavities:
            # Approximation for ultr-relativistic electrons
            cav.harmonic_number = int(cav.frequency/(scipy.constants.c/self.get_total_length()))

    @classmethod
    def from_madx_seqfile(cls, seq_file, seq_name, energy, particle_type='electron'):
        madx = cpymad_lattice_conv.from_madx_seqfile(seq_file, energy, particle_type)
        return cls.from_cpymad(madx, seq_name)

    @classmethod
    def from_cpymad(cls, madx, seq_name, dependencies=False):
        if dependencies:
            xdeps_manager, element_seq = cpymad_lattice_conv.from_cpymad_with_dependencies(madx, seq_name)
            return cls(seq_name, element_seq, key='sequence', xdeps_manager=xdeps_manager) 
        else:
            _, element_seq = cpymad_lattice_conv.from_cpymad(madx, seq_name)
            return cls(seq_name, element_seq, key='sequence') 

    @classmethod
    def from_sad(cls, sad_lattice, seq_name, momentum):
        madx = sad_lattice_conv.from_sad_to_madx(sad_lattice, momentum)
        return cls.from_cpymad(madx, seq_name)

    @classmethod
    def from_pyat(cls, pyat_lattice):
        seq = pyat_lattice_conv.from_pyat(pyat_lattice)
        return cls(pyat_lattice.name, seq, energy=pyat_lattice.energy*1e-9) 

    def to_cpymad(self):
        return cpymad_lattice_conv.to_cpymad(self.name, self.params['energy'], self.sequence)

    def to_pyat(self):
        self._update_cavity_energy()
        self._update_harmonic_number()
        return pyat_lattice_conv.to_pyat(self.name, self.params['energy']*1e9, self.line)

    def to_xline(self):
        xline_lattice_conv.to_xline(self.sliced.line) 

    def optics(self, engine='madx', drop_drifts=False):
        """
        Calculate optics 

        Key Args:
            engine : string, desired engine: madx, pyat
            drop_drifts : Boolean, return output with (TRUE) or without (FALSE) drifts
        Returns:
            Pandas DataFrame of calculated optics
        """
        if engine == 'madx':
            cpymad_instance = self.to_cpymad()
            cpymad_instance.use(self.name)
            cpymad_instance.twiss(sequence=self.name)
            tw = cpymad_instance.table.twiss.dframe().copy()
            tw.name = [element[:-2] for element in tw.name]
            tw.set_index('name', inplace=True)
        if engine == 'pyat':
            pyat_instance = self.to_pyat()
            lin = pyat_functions.calc_optics_pyat(pyat_instance)
            tw = pyat_functions.pyat_optics_to_pandas_df(pyat_instance, lin)
            tw.set_index('name', inplace=True)
            tw.index = np.roll(tw.index, 1)
            tw.keyword = np.roll(tw.keyword, 1)

        if drop_drifts:
            tw = tw.drop(tw[tw['keyword']=='drift'].index)
        return tw 

    def remove_elements(self, index=None, names=None):
        if index:
            mask = np.ones(len(self.sequence), dtype=bool)        
            for idx in index:
                mask[idx] = False
            self.sequence = np.array(self.sequence)[mask] 
        elif names:
            mask = np.ones(len(self.sequence), dtype=bool)
            for el_idx, element in enumerate(self.sequence):
                if element.name in names:
                    mask[el_idx] = False
            self.sequence = np.array(self.sequence)[mask]

    def get_class(self, class_type: xe.BaseElement) -> List[xe.BaseElement]:
        """ Get list of elements matching given class """
        return [self.line[element] for element in self.line if isinstance(self.line[element], class_type)]

    def convert_sbend_to_rbend(self):
        """ Convert all rbends to sbends in sequence """
        self.sequence = [element.convert_to_rbend() if element.__class__.__name__ == 'Sbend' else element for element in self.sequence]

    def convert_rbend_to_sbend(self):
        """ Convert all rbends to sbends in sequence """
        self.sequence = [element.convert_to_sbend() if element.__class__.__name__ == 'Rbend' else element for element in self.sequence]

    def slice_lattice(self):
        thin_list = [el.slice_element() for el in self.sequence]
        thin_list = [item for sublist in thin_list for item in sublist]
        return {el.name:el for el in thin_list}

    @property
    def sliced(self):
        return Lattice(self.name, self.slice_lattice(), key='sequence')

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, sequence = {self.sequence.names})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, sequence = {self.sequence.names})"
