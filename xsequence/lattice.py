"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import os, sys
import scipy.constants
import numpy as np
import pandas as pd
from xsequence.lattice_baseclasses import Line, Sequence, Beam

class Lattice:
    """ A class used to represent an accelerator lattice """
    def __init__(self, name: str, element_dict: dict, key: str = 'line', **kwargs):
        self.name = name
        self.beam = Beam(energy=kwargs.pop('energy', None), particle=kwargs.pop('particle', None))

        if key == 'line':
            self.line = Line(element_dict)
        elif key == 'sequence':
            self.sequence = Sequence(element_dict)

        if 'xdeps_manager' in kwargs:
            self.manager = kwargs['xdeps_manager']
            self.vref = kwargs['vref']
            self.mref = kwargs['mref']
            self.sref = kwargs['sref']

    @property
    def line(self):
        return self._line
    
    @line.setter
    def line(self, line):
        self._line = line
        self._sequence = line._get_sequence()

    @property
    def sequence(self):
        return self._sequence
    
    @sequence.setter
    def sequence(self, sequence):
        self._sequence = sequence
        self._line = sequence._get_line()

    def get_total_length(self) -> float:
        return self.sequence._get_total_length()

    def _update_cavity_energy(self):
        for cav in self.sequence.get_class('RFCavity'):
            self.sequence[cav].energy = self.beam.energy

    def _update_harmonic_number(self):
        for cav in self.sequence.get_class('RFCavity'):
            # Approximation for ultr-relativistic electrons
            self.sequence[cav].harmonic_number = int(self.sequence[cav].frequency*1e6/(scipy.constants.c/self.get_total_length()))

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

    def convert_sbend_to_rbend(self):
        """ Convert all rbends to sbends in sequence """
        self.sequence = Sequence({el:val.convert_to_rbend() if el.__class__.__name__ == 'SectorBend' else val for el, val in self.sequence.items()})

    def convert_rbend_to_sbend(self):
        """ Convert all rbends to sbends in sequence """
        self.sequence = Sequence({el:val.convert_to_sbend() if el.__class__.__name__ == 'RectangularBend' else val for el, val in self.sequence.items()})
    
    def _slice_lattice(self):
        thin_list = [el.slice_element() for name, el in self.sequence.items()]
        thin_list = [item for sublist in thin_list for item in sublist]
        return {el.name:el for el in thin_list}

    @property
    def sliced(self):
        return Lattice(self.name, self._slice_lattice(), key='sequence')

    def __str__(self):
        return f"{self.__class__.__name__}({self.name}, sequence = {self.sequence.names})"

    def __repr__(self):
        return f"{self.__class__.__name__}({self.name}, sequence = {self.sequence.names})"
