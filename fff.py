# Framework For FCC-ee (FFF) a.k.a. f3 , fcubed

import os
import elements
import conversion_functions as cf


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

    def __init__(self, name, sequence, key='line', **kwargs):
        self.name = name
        self.key = key
        self.energy = kwargs.pop('energy', 0.0)
        if key == 'line':
            self._sequence_with_drifts = sequence
            self._calc_s_positions()
            self._convert_line_to_sequence()
        elif key == 'sequence':
            self._sequence = sequence
            self._convert_sequence_to_line()

    def _convert_line_to_sequence(self):
        elements_only = [ele for ele in self._sequence_with_drifts or self.__class__.__name__ != 'Drift']
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
        self._sequence_with_drifts = sequence_w_drifts
    
    def _calc_s_positions(self):
        previous_end = 0.0
        positions = []
        for element in self._sequence_with_drifts:
            pos = previous_end + element.length/2.
            element.pos = pos
            previous_end += element.length
    
    def _get_s_positions(self, reference='center'):
        if reference == 'center': 
            return [element.pos for element in self._sequence]
        elif reference == 'start': 
            return [element.pos-element.length/2. for element in self._sequence]
        elif reference == 'end': 
            return [element.pos+element.length/2. for element in self._sequence]

    @property
    def sequence(self):
        return ElementList(self._sequence)

    @property
    def sequence_with_drifts(self):
        return ElementList(self._sequence_with_drifts)
    
    @property
    def positions(self):
        self._calc_s_positions()
        return self._get_s_positions()

    @property
    def start_positions(self):
        return self._get_s_positions(reference='start')

    @property
    def end_positions(self):
        return self._get_s_positions(reference='end')

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
        args_str = [f"'{self.name}'", f'{self.elements}', f"key='{self.key}'"] 
        return f"{self.__class__.__name__}({', '.join(args_str)})"

    def __repr__(self):
        args_str = [f"'{self.name}'", f'{self._sequence}', f"key='{self.key}'"] 
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



