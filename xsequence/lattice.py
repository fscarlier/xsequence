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

    @classmethod
    def from_madx_seqfile(cls, seq_file, seq_name, energy=None, dependencies=False, particle_type='electron'):
        from xsequence.conversion_utils.cpymad import cpymad_lattice_conv
        
        madx = cpymad_lattice_conv.from_madx_seqfile(seq_file, energy, particle_type)
        return cls.from_cpymad(madx, seq_name, energy=energy, dependencies=dependencies)

    @classmethod
    def from_cpymad(cls, madx, seq_name, energy=None, dependencies=False):
        from xsequence.conversion_utils.cpymad import cpymad_lattice_conv
        
        if dependencies:
            xdeps_manager, vref, mref, sref, element_seq = cpymad_lattice_conv.from_cpymad_with_dependencies(madx, seq_name)
            return cls(seq_name, element_seq, energy=energy, key='sequence', vref=vref, mref=mref, sref=sref, xdeps_manager=xdeps_manager) 
        else:
            _, element_seq = cpymad_lattice_conv.from_cpymad(madx, seq_name)
            return cls(seq_name, element_seq, energy=energy, key='sequence') 

    @classmethod
    def from_sad(cls, sad_lattice, seq_name, energy=None):
        from xsequence.conversion_utils.sad import sad_lattice_conv
        
        madx = sad_lattice_conv.from_sad_to_madx(sad_lattice, energy)
        return cls.from_cpymad(madx, seq_name, energy=energy)

    @classmethod
    def from_pyat(cls, pyat_lattice):
        from xsequence.conversion_utils.pyat import pyat_lattice_conv
        
        seq = pyat_lattice_conv.from_pyat(pyat_lattice)
        return cls(pyat_lattice.name, seq, energy=pyat_lattice.energy*1e-9) 

    def to_cpymad(self):
        from xsequence.conversion_utils.cpymad import cpymad_lattice_conv
        
        return cpymad_lattice_conv.to_cpymad(self.name, self.beam.energy, self.sequence)

    def to_pyat(self):
        from xsequence.conversion_utils.pyat import pyat_lattice_conv
        
        self._update_cavity_energy()
        self._update_harmonic_number()
        return pyat_lattice_conv.to_pyat(self.name, self.beam.energy*1e9, self.line)

    def to_bmad(self, file_path=None):
        from xsequence.conversion_utils.bmad import bmad_lattice_conv
        
        if file_path:
            f = open(file_path, "w")
            f.write(bmad_lattice_conv.to_bmad(self.name, self.beam, self.line))
            f.close()
        else:
            return bmad_lattice_conv.to_bmad(self.name, self.beam, self.line) 

    def to_xline(self):
        from xsequence.conversion_utils.xline import xline_lattice_conv
        
        xline_lattice_conv.to_xline(self.sliced.line) 

    def optics(self, engine='madx', drop_drifts=True, pyat_idx_to_mad=False):
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
            tw['name'] = [nn[:-2] for nn in tw['name']]
            tw.set_index('name', inplace=True)
            if drop_drifts:
                tw = tw.drop(tw[tw['keyword']=='drift'].index)
            return tw 
        if engine == 'pyat':
            from xsequence.helpers import pyat_functions
            
            pyat_instance = self.to_pyat()
            lin = pyat_functions.calc_optics_pyat(pyat_instance)
            tw = pyat_functions.pyat_optics_to_pandas_df(pyat_instance, lin)
            if pyat_idx_to_mad:
                tw.name = np.roll(tw.name, 1)
                tw.keyword = np.roll(tw.keyword, 1)
            tw.set_index('name', inplace=True)
            if drop_drifts:
                tw = tw.drop(tw[tw['keyword']=='drift'].index)
            return tw 
        if engine == "bmad":
            bmad_file = "temporary_lattice_for_twiss.bmad"
            self.to_bmad(file_path=bmad_file)

            TAO_PYTHON_DIR=os.environ['ACC_ROOT_DIR'] + '/tao/python'
            sys.path.insert(0, TAO_PYTHON_DIR)
            
            import pytao
            from io import StringIO

            tao = pytao.Tao()
            tao.init(f"-noinit -noplot -lattice_file {bmad_file}")
            bmad_twiss = tao.cmd('show lattice -python -all -custom bmad_custom.twiss')
            tw = pd.read_csv(StringIO("\n".join(line for line in bmad_twiss)), sep=';')
            col_types = tw.iloc[0]
            tw.drop([0], inplace=True)
            
            tw = tw[tw['name'] != 'BEGINNING']
            tw = tw[tw['name'] != 'END']
            
            for col in tw:
                if col_types[col] == 'INT':
                    tw[col] = tw[col].astype(int)
                elif col_types[col] == 'REAL':
                    tw[col] = tw[col].astype(float)
                elif col_types[col] == 'STR':
                    tw[col] = tw[col].str.lower()

            tw.set_index('name', inplace=True)
            tw.drop(columns=['index'], inplace=True)

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
