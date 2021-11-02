"""
Module fsf.lattice_baseclasses
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base element dataclasses for particle accelerator elements.
"""

from collections import OrderedDict
import fsf.elements as xe


def _key_to_idx_slice(names, key):
    if key.start:
        start_idx = names.index(key.start)
    else:
        start_idx = 0
    if key.stop:
        stop_idx = names.index(key.stop)
    else:
        stop_idx = len(names)
    return slice(start_idx, stop_idx)


class ElementDict(OrderedDict):
    @property
    def names(self):
        return [self[element].name for element in self]
    
    @property
    def positions(self):
        return [self[element].position_data.position for element in self]

    def get_last_element(self):
        return self[self.names[-1]]    

    def get_s_positions(self, reference='center'):
        if reference == 'center': 
            return [self[name].position_data.position for name in self.names]
        elif reference == 'start': 
            return [self[name].position_data.start for name in self.names]
        elif reference == 'end': 
            return [self[name].position_data.end for name in self.names]

    def get_range_s(self, start_pos: float, end_pos: float):
        start_name = next(idx for idx, name in enumerate(self.names) if self[name].position_data.start > start_pos)
        stop_name = 1 + next(idx for idx, name in enumerate(self.names) if self[name].position_data.end > end_pos)
        return self[start_name:stop_name]
    
    def _get_total_length(self):
        return self[self.names[-1]].position_data.end

    def _get_names(self):
        return list(self.keys())
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            names = self._get_names()
            if isinstance(key.start, str):
                key = _key_to_idx_slice(names, key)
            names = names[key]
            return ElementDict({name:self[name] for name in names})
        else:
            if isinstance(key, int):
                return self[self.names[key]]
            else:
                return super().__getitem__(key)

class Line(ElementDict):
    def _set_positions(self):
        """ Calculate longitudinal positions of elements from line representation """
        previous_end = 0.0
        for name, element in self.items():
            element.position_data.set_position(location=previous_end+element.length/2.) 
            previous_end += element.length

    def _get_sequence(self):
        self._set_positions()
        return Sequence({k:self[k] for k in self if not isinstance(self[k], xe.Drift)})


class Sequence(ElementDict):
    def _get_line(self):
        """ Convert sequence representation to line representation including drifts """
        previous_end = self[self._get_names()[0]].position_data.start
        drift_count = 0
        line_w_drifts = OrderedDict()
        for name, element in self.items():
            element_start = element.position_data.start
            if element_start > previous_end:
                drift_length = element_start-previous_end
                drift_pos = previous_end + drift_length/2.
                drift_name = f'drift_{drift_count}'
                line_w_drifts[drift_name] = xe.Drift(drift_name, length=drift_length, location=drift_pos)
                drift_count += 1
            elif element_start < previous_end-1e-9: # Tolerance for rounding
                raise ValueError(f'Negative drift at element {element.name}')

            line_w_drifts[name] = element
            previous_end = element.position_data.end
        return Line(line_w_drifts)


