# Framework For FCC-ee (FFF) a.k.a. f3 , fcubed

import os
from lattice import elements
import lattice.conversion_functions as cf
import toolkit.pyat_functions as pf

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
            key: string
                'line' for element_list including explicit drifts
                'sequence' for element_list without explicit drifts
            energy : float
                reference energy of lattice
        """
        self.name = name
        self.key = key
        self.energy = kwargs.pop('energy', 0.0)
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
                sequence_w_drifts.append(elements.Drift(f'drift_{drift_count}', 
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

    
    def export(self, code='cpymad'):
        """
        Export lattice to specific code

        Args:
            code : string
                desired export code: madx, pyat
        """
        if code == 'cpymad':
            return cf.export_cpymad_from_fff(self)
        elif code == 'pyat':
            return cf.export_pyat_from_fff(self)


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
            cpymad_instance = cf.export_cpymad_from_fff(self)
            cpymad_instance.use(self.name)
            cpymad_instance.twiss(sequence=self.name)
            tw = cpymad_instance.table.twiss.dframe().copy()
            tw.name = [element[:-2] for element in tw.name]
        if engine == 'pyat':
            pyat_instance = cf.export_pyat_from_fff(self)
            lin = pf.calc_optics_pyat(pyat_instance)
            tw = pf.pyat_optics_to_pandas_df(pyat_instance, lin)
        
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
        args_str = [f"'{self.name}'", f"{self.elements}", f"key='{self.key}'"] 
        return f"{self.__class__.__name__}({', '.join(args_str)})"


    def __repr__(self):
        args_str = [f"'{self.name}'", f"{self._sequence}", f"key='{self.key}'"] 
        return f"{self.__class__.__name__}({', '.join(args_str)})"
