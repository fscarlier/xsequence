import scipy, copy, at
import fsf.elements
import numpy as np
from cpymad.madx import Madx
from toolkit import pyat_functions
from conversion_utils import pyat_conv, cpymad_conv

class Lattice():
    """
    A class used to represent an accelerator lattice 
    """

    def __init__(self, name, element_list, key='line', **kwargs):
        """
        Args:
            name : string
                name of lattice
            element_list: iterable
                list of accelerator elements
        
        Key Args:
            key: string
                'line' for element_list including explicit drifts
                'sequence' for element_list without explicit drifts
        """
        self.name = name
        self.key = key
        self.energy = kwargs.pop('energy', 0.0)
        self.global_elements = kwargs.pop('global_elements', None)
        if key == 'line':
            self.line = element_list
        elif key == 'sequence':
            self.sequence = element_list


    def _convert_line_to_sequence(self):
        """
        Convert line representation to sequence representation
        """
        elements_only = [ele for ele in self._line or self.__class__.__name__ != 'Drift']
        self._sequence = elements_only


    def _convert_sequence_to_line(self):
        """
        Convert sequence representation to line representation including drifts
        """
        previous_end = 0.0
        drift_count = 0
        sequence_w_drifts = []
        for element in self._sequence:
            element_start = element.pos-element.length/2.
            if element_start > previous_end:
                drift_length = element_start-previous_end
                drift_pos = previous_end + drift_length/2.
                sequence_w_drifts.append(fsf.elements.Drift(f'drift_{drift_count}', 
                                length=drift_length, pos=drift_pos))
                drift_count += 1
            elif element_start < previous_end-1e-9: # Tolerance for rounding
                print(element.name, element.pos, element.pos-element.length/2.)
                print(previous_end)
                raise ValueError(f'Negative drift at element {element.name}')

            sequence_w_drifts.append(element)
            previous_end = element.pos + element.length/2.
        self._line = sequence_w_drifts


    def _calc_s_positions(self):
        """
        Calculate longitudinal positions of elements from line representation
        """
        previous_end = 0.0
        positions = []
        for element in self._line:
            pos = previous_end + element.length/2.
            element.pos = pos
            previous_end += element.length

    
    def get_s_positions(self, reference='center'):
        """
        Key args:
            reference : string
                reference location of s position at element
        
        Returns:
            List of longitudinal positions of each element excluding drifts
        """
        if reference == 'center': 
            return [element.pos for element in self._sequence]
        elif reference == 'start': 
            return [element.pos-element.length/2. for element in self._sequence]
        elif reference == 'end': 
            return [element.pos+element.length/2. for element in self._sequence]

    
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
            element_list : iterable
                list of accelerator elements
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
        Set line and update instance

        Args:
            element_list : iterable
                list of accelerator elements including drifts
        """
        self._line = element_list
        self._calc_s_positions()
        self._convert_line_to_sequence()


    @property
    def total_length(self):
        return self.line[-1].pos + self.line[-1].length/2.


    def get_element_names(self):
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
        return self.get_range_s(start_element[0].pos, end_element[0].pos)


    def update_cavity_energy(self):
        cavities = self.get_class('RFCavity')
        for cav in cavities:
            cav.energy = self.energy


    def update_harmonic_number(self):
        cavities = self.get_class('RFCavity')
        for cav in cavities:
            # Approximation for ultr-relativistic electrons
            cav.harmonic_number = int(cav.freq*1e6/(scipy.constants.c/self.total_length))


    @classmethod
    def from_madx_seqfile(cls, seq_file, seq_name, energy, particle_type='electron'):
        """
        Import lattice from MAD-X sequence file

        Args:
            seqfile: string
                path to madx sequence
            seqname: string
                name of madx sequence
            energy: int
                energy of beam in GeV
        Key args:
            particle_type: string
                type of particle, 'electron' 'proton' ...
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
            seq_name: string
                name of madx sequence
        """
        madx.use(seq_name)
        total_length = madx.sequence[seq_name].elements[-1].at
        element_seq = list(map(cpymad_conv.convert_cpymad_element_to_fsf, 
                               madx.sequence[seq_name].elements))
        return cls(seq_name, element_seq, key='sequence', 
                   energy=madx.sequence[seq_name].beam.energy) 


    @classmethod
    def from_pyat(cls, pyat_lattice):
        """
        Export lattice to pyat
        """
        total_length = pyat_lattice.get_s_pos([-1])
        seq = []
        for el in pyat_lattice:
            new_element = pyat_conv.convert_pyat_element_to_fsf(el)
            seq.append(new_element)
        return cls(pyat_lattice.name, seq, energy=pyat_lattice.energy*1e-9) 


    def to_cpymad(self):
        """
        Export lattice to cpymad
        """
        madx = Madx()
        madx.option(echo=False, info=False, debug=False)
        seq_command = ''
        
        elements = self.sequence
        for element in elements[1:-1]:
            element.to_cpymad(madx)
            seq_command += f'{element.name}, at={element.pos}  ;\n'
        
        madx.input(f'{self.name}: sequence, refer=centre, l={self.sequence[-1].pos};')
        madx.input(seq_command)
        madx.input('endsequence;')
        madx.command.beam(particle='electron', energy=self.energy)
        return madx


    def to_pyat(self):
        """
        Export lattice to pyat
        """
        self.update_cavity_energy()
        self.update_harmonic_number()
        elements = self.line
        seq = []
        for element in elements:
            pyat_el = element.to_pyat() 
            seq.append(pyat_el)
        pyat_lattice = at.Lattice(seq, name=self.name, key='ring', energy=self.energy*1e9)
        return pyat_lattice


    def optics(self, engine='madx', drop_drifts=False):
        """
        Calculate optics 

        Key Args:
            engine : string
                desired engine: madx, pyat
            drop_drifts : Boolean
                return output with (TRUE) or without (FALSE) drifts
        
        Returns:
            Pandas DataFrame of calculated optics
        """
        if engine == 'madx':
            cpymad_instance = self.to_cpymad()
            cpymad_instance.use(self.name)
            cpymad_instance.twiss(sequence=self.name)
            tw = cpymad_instance.table.twiss.dframe().copy()
            tw.name = [element[:-2] for element in tw.name]
        if engine == 'pyat':
            pyat_instance = self.to_pyat()
            lin = pyat_functions.calc_optics_pyat(pyat_instance)
            tw = pyat_functions.pyat_optics_to_pandas_df(pyat_instance, lin)
        #TODO: cycle through elements to show at start or end of element for all engines
        if drop_drifts:
            tw = tw.drop(tw[tw['keyword']=='drift'].index)
        tw.set_index('name', inplace=True)
        return tw 

    
    def get_element(self, element_name):
        """
        Get list of elements matching given name 

        Args:
            element_name : string
                Name of desired element
        
        Returns:
            List of elements matching given name
        """
        return [element for element in self._line if element.name == element_name]


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


    def get_class(self, class_name):
        """
        Get list of elements matching given class 

        Args:
            class_name : string
                Name of desired class
        
        Returns:
            List of elements matching given class
        """
        return [element for element in self._line if element.__class__.__name__ == class_name]


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


    def save(self):
        return

    
    def copy(self):
        return

    
    def clone(self):
        return


    def invert(self):
        return


    def extract(self):
        return


    def __str__(self):
        args_str = [f"'{self.name}'", f"{self._sequence}", f"key='{self.key}'"] 
        return f"{self.__class__.__name__}({', '.join(args_str)})"


    def __repr__(self):
        args_str = [f"'{self.name}'", f"{self._sequence}", f"key='{self.key}'"] 
        return f"{self.__class__.__name__}({', '.join(args_str)})"
