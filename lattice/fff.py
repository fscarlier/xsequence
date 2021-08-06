# Framework For FCC-ee (FFF) a.k.a. f3 , fcubed

import os
from lattice import elements
import lattice.conversion_functions as cf
import toolkit

class Lattice():
    """
    A class used to represent an accelerator lattice 

    Attributes
    ----------
    name : string
        name of lattice
    sequence: iterable
        list of accelerator elements
    energy : float
        reference energy of lattice
    
    Methods
    -------
    """

    def __init__(self, name, element_list, key='line', **kwargs):
        self.name = name
        self.key = key
        self.energy = kwargs.pop('energy', 0.0)
        if key == 'line':
            self.line = element_list
        elif key == 'sequence':
            self.sequence = element_list

    def _convert_line_to_sequence(self):
        elements_only = [ele for ele in self._line or self.__class__.__name__ != 'Drift']
        self._sequence = elements_only

    def _convert_sequence_to_line(self):
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
        previous_end = 0.0
        positions = []
        for element in self._line:
            pos = previous_end + element.length/2.
            element.pos = pos
            previous_end += element.length
    
    def get_s_positions(self, reference='center'):
        if reference == 'center': 
            return [element.pos for element in self._sequence]
        elif reference == 'start': 
            return [element.pos-element.length/2. for element in self._sequence]
        elif reference == 'end': 
            return [element.pos+element.length/2. for element in self._sequence]

    @property
    def elements(self):
        return ElementList(self._sequence)
    
    @property
    def sequence(self):
        return self._sequence

    @sequence.setter
    def sequence(self, element_list):
        self._sequence = element_list
        self._convert_sequence_to_line()
    
    @property
    def line(self):
        return self._line

    @line.setter
    def line(self, element_list):
        self._line = element_list
        self._calc_s_positions()
        self._convert_line_to_sequence()
    
    def export(self, code='cpymad'):
        if code == 'cpymad':
            return cf.export_cpymad_from_fff(self)
        elif code == 'pyat':
            return cf.export_pyat_from_fff(self)

    def optics(self, engine='madx', tofile=None, drop_drifts=False):
        if engine == 'madx':
            cpymad_instance = cf.export_cpymad_from_fff(self)
            cpymad_instance.use(self.name)
            cpymad_instance.twiss(sequence=self.name)
            tw = cpymad_instance.table.twiss.dframe().copy()
            tw.name = [element[:-2] for element in tw.name]
        if engine == 'pyat':
            pyat_instance = cf.export_pyat_from_fff(self)
            lin = toolkit.pyat_functions.calc_optics_pyat(pyat_instance)
            tw = toolkit.pyat_functions.pyat_optics_to_pandas_df(pyat_instance, lin)
        
        if drop_drifts:
            tw = tw.drop(tw[tw['keyword']=='drift'].index)
        tw.set_index('name', inplace=True)
        return tw 
    
    def get_element(self, element_name):
        return [element for element in self._line if element.name == element_name]

    def get_class(self, class_name):
        return [element for element in self._line if element.__class__.__name__ == class_name]

    def convert_rbend_to_sbend(self):
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


class ElementList():

    def __init__(self, sequence):
        self._sequence = sequence
        self.update_elements()

    def update_elements(self):
        for ele in self._sequence:
            setattr(self, ele.name, ele)

    def get_element_names(self):
        return [element.name for element in self._sequence]

    def __repr__(self):
        return '[{}]'.format(', '.join(
            self.get_element_names()))



