"""
Module fsf.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import scipy, at
import fsf.elements
import numpy as np
from cpymad.madx import Madx
from fsf.helpers import pyat_functions
import xline as xl
from collections import defaultdict


class Lattice:
    """
    A class used to represent an accelerator lattice 
    """
    def __init__(self, name, element_list, key='line', **kwargs):
        """
        Args:
            name : string, name of lattice
            element_list: iterable, list of accelerator elements
        Key Args:
            key: string
                'line' for element_list including explicit drifts
                'sequence' for element_list without explicit drifts
        """
        self.name = name
        self.params = {'key':key, 'energy':kwargs.pop('energy', 0.0)}
        self._set_lattice(element_list)
        self._update(**kwargs)

    def _set_lattice(self, element_list):
        if self.params['key'] == 'line':
            self.line = element_list
        elif self.params['key'] == 'sequence':
            self.sequence = element_list
    
    def _update(self, **kwargs):
        for (key, value) in kwargs.items():
            setattr(self, key, value)

    def _convert_line_to_sequence(self):
        """
        Convert line representation to sequence representation
        """

        elements_only = [ele for ele in self._line if ele.__class__.__name__ != 'Drift' ]
        self._sequence = elements_only

    def _convert_sequence_to_line(self):
        """
        Convert sequence representation to line representation including drifts
        """
        assert self.sequence[0].__class__.__name__ == 'Marker', "Start element of sequence should be Marker element"
        assert self.sequence[-1].__class__.__name__ == 'Marker', "Last element of sequence should be Marker element"

        previous_end = self.sequence[0].position_data.end
        drift_count = 0
        line_w_drifts = [self.sequence[0]]
        for element in self.sequence[1:]:
            element_start = element.position_data.start
            if element_start > previous_end:
                drift_length = element_start-previous_end
                drift_pos = previous_end + drift_length/2.
                line_w_drifts.append(fsf.elements.Drift(f'drift_{drift_count}', 
                                length=drift_length, pos=drift_pos))
                drift_count += 1
            elif element_start < previous_end-1e-9: # Tolerance for rounding
                raise ValueError(f'Negative drift at element {element.name}')

            line_w_drifts.append(element)
            previous_end = element.position_data.end
        self._line = line_w_drifts

    def _calc_s_positions(self):
        """
        Calculate longitudinal positions of elements from line representation
        """
        previous_end = 0.0
        for element in self._line:
            element.position_data.set_position(location=previous_end+element.length/2.) 
            previous_end += element.length

    def get_s_positions(self, reference='center'):
        """
        Key args:
            reference : string, reference location of s position at element
        Returns:
            List of longitudinal positions of each element excluding drifts
        """
        if reference == 'center': 
            return [element.position_data.position for element in self._sequence]
        elif reference == 'start': 
            return [element.position_data.start for element in self._sequence]
        elif reference == 'end': 
            return [element.position_data.end for element in self._sequence]

    @property
    def sequence(self):
        """
        List of elements in model
        """
        return self._sequence

    @sequence.setter
    def sequence(self, element_list):
        """
        Set sequence and update instance

        Args:
            element_list : iterable, list of accelerator elements
        """
        self._sequence = element_list
        self._convert_sequence_to_line()

    @property
    def line(self):
        """
        List of elements in model including drifts
        """
        return self._line

    @line.setter
    def line(self, element_list):
        """
        Set line and update sequence

        Args:
            element_list : list, list of accelerator elements including drifts
        """
        self._line = element_list
        self._calc_s_positions()
        self._convert_line_to_sequence()

    @property
    def total_length(self):
        return self.line[-1].position_data.end

    def get_element_names(self, key='sequence'):
        if key == 'sequence':
            self.names = [el.name for el in self.sequence]
        if key == 'line':
            self.names = [el.name for el in self.line]
        return self.names 
        
    def get_range_s(self, start_pos, end_pos):
        seq_start = np.array(self.get_s_positions(reference='start'))
        seq_end = np.array(self.get_s_positions(reference='end'))
        idx = np.array( np.where((seq_end >= start_pos) & (seq_start <= end_pos))[0] )
        return idx, self._sequence[idx[0]:idx[-1]+1]

    def get_range_elements(self, start_element, end_element):
        start_element = self.get_element(start_element)
        end_element = self.get_element(end_element)
        assert len(start_element) == 1, "Cannot find range: Multiple elements with same start name"
        assert len(end_element) == 1, "Cannot find range: Multiple elements with same end name"
        return self.get_range_s(start_element[0].position_data.position, end_element[0].position_data.position)

    def update_cavity_energy(self):
        cavities = self.get_class('RFCavity')
        for cav in cavities:
            cav.energy = self.params['energy']

    def update_harmonic_number(self):
        cavities = self.get_class('RFCavity')
        for cav in cavities:
            # Approximation for ultr-relativistic electrons
            cav.harmonic_number = int(cav.rf_data.frequency/(scipy.constants.c/self.total_length))

    @classmethod
    def from_madx_seqfile(cls, seq_file, seq_name, energy, particle_type='electron'):
        """
        Import lattice from MAD-X sequence file

        Args:
            seqfile: string, path to madx sequence
            seqname: string, name of madx sequence
            energy: int, energy of beam in GeV
        Key args:
            particle_type: string, type of particle, 'electron' 'proton' ...
        """
        madx = Madx()
        madx.option(echo=False, info=False, debug=False)
        madx.call(file=seq_file)
        madx.input('SET, FORMAT="25.20e";')
        madx.command.beam(particle=particle_type, energy=energy)
        return cls.from_cpymad(madx, seq_name)

    @classmethod
    def from_cpymad(cls, madx, seq_name):
        """
        Import lattice from cpymad sequence

        Args:
            madx: cpymad.madx Madx() instance
            seq_name: string, name of madx sequence
        """
        def convert_cpymad_element_to_fsf(element):
            base_type = element.base_type.name
            return fsf.elements.CPYMAD_TO_FSF_MAP[base_type].from_cpymad(element)
        
        madx.use(seq_name)
        element_seq = list(map(convert_cpymad_element_to_fsf, 
                               madx.sequence[seq_name].elements))
        
        variables=defaultdict(lambda :0)
        for name,par in madx.globals.cmdpar.items():
            variables[name]=par.value
        
        return cls(seq_name, element_seq, key='sequence', 
                   energy=madx.sequence[seq_name].beam.energy, global_variables=variables) 

    @classmethod
    def from_pyat(cls, pyat_lattice):
        def convert_pyat_element_to_fsf(element):
            base_type = element.__class__.__name__
            return fsf.elements.PYAT_TO_FSF_MAP[base_type].from_pyat(element)

        seq = []
        for el in pyat_lattice:
            new_element = convert_pyat_element_to_fsf(el)
            seq.append(new_element)
        return cls(pyat_lattice.name, seq, energy=pyat_lattice.energy*1e-9) 

    def to_cpymad(self):
        madx = Madx()
        madx.option(echo=False, info=False, debug=False)
        seq_command = ''
        
        elements = self.sequence
        for element in elements[1:-1]:
            element.to_cpymad(madx)
            seq_command += f'{element.name}, at={element.position_data.position}  ;\n'
        
        madx.input(f'{self.name}: sequence, refer=centre, l={self.sequence[-1].position_data.end};')
        madx.input(seq_command)
        madx.input('endsequence;')
        madx.command.beam(particle='electron', energy=self.params['energy'])
        return madx

    def to_pyat(self):
        self.update_cavity_energy()
        self.update_harmonic_number()
        seq = [element.to_pyat() for element in self.line]
        pyat_lattice = at.Lattice(seq, name=self.name, key='ring', energy=self.params['energy']*1e9)
        for cav in at.get_elements(pyat_lattice, at.RFCavity):
            cav.Frequency = cav.HarmNumber*scipy.constants.c/pyat_lattice.circumference 
        return pyat_lattice

    def to_xline(self):
        names =  self.sliced.get_element_names(key='line')
        line = [el.to_xline() for el in self.sliced.line]
        xline_lattice = xl.Line(elements=line, element_names=names)
        return xline_lattice

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

    def get_element(self, element_names):
        """
        Get list of elements matching given name 

        Args:
            element_name : string or list of strings, Name of desired element
        Returns: 
            List of elements matching given name
        """
        if isinstance(element_names, str):
            return [element for element in self._line if element.name == element_names]
        if isinstance(element_names, list):
            return [element for element in self._line if element.name in element_names]

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

    def get_class(self, class_names):
        """
        Get list of elements matching given class 

        Args:
            class_name : array of strings
                Names of desired classes
        
        Returns:
            List of elements matching given class
        """
        return [element for element in self._line if element.__class__.__name__ in class_names]

    def convert_sbend_to_rbend(self):
        """
        Convert all rbends to sbends in sequence 
        """
        self.sequence = [element.convert_to_rbend() if element.__class__.__name__ == 'Sbend' else element for element in self.sequence]

    def convert_rbend_to_sbend(self):
        """
        Convert all rbends to sbends in sequence 
        """
        self.sequence = [element.convert_to_sbend() if element.__class__.__name__ == 'Rbend' else element for element in self.sequence]

    def slice_lattice(self):
        thin_list = [el.slice_element() for el in self.sequence]
        self._thin_sequence = [item for sublist in thin_list for item in sublist]
        return self._thin_sequence

    @property
    def sliced(self):
        try: 
            return Lattice(self.name, self._thin_sequence, key='sequence')
        except AttributeError:
            self.slice_lattice()
            return Lattice(self.name, self._thin_sequence, key='sequence')

    def __str__(self):
        args_str = [f"'{self.name}'", f"{self._sequence}", f"key='{self.params['key']}'"] 
        return f"{self.__class__.__name__}({', '.join(args_str)})"

    def __repr__(self):
        args_str = [f"'{self.name}'", f"{self._sequence}", f"key='{self.params['key']}'"] 
        return f"{self.__class__.__name__}({', '.join(args_str)})"
