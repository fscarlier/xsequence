"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import os 
from xsequence.helpers.sad_templates.sad_templates import SadTemplates
from xsequence.conversion_utils.cpymad import cpymad_lattice_conv

def from_sad_to_madx(sad_lattice, momentum, particle_type='electron'):
    temp_mad_path = "temporary_mad"
    create_madx_seq_from_sad(sad_lattice, temp_mad_path, momentum)
    temp_mad_path_seq = "temporary_mad.seq"
    madx = cpymad_lattice_conv.from_madx_seqfile(temp_mad_path_seq, 'ring', momentum/1e9)
    os.remove(temp_mad_path_seq)
    return madx

    
def create_madx_seq_from_sad(sad_seq_path, mad_seq_path, momentum):
    sm = SadTemplates(path_to_sad_sequence=sad_seq_path, momentum=momentum)
    sm.convert_to_madx(madx_output_file=mad_seq_path)


