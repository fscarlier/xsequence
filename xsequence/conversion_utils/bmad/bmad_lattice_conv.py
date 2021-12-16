"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

def to_bmad(seq_name, beam, line):
    assert beam.energy
    assert beam.particle

    beam_str = f"beam, energy = {beam.energy} \nparameter[particle] = {beam.particle}\n"
    elements_str = ""
    
    for _, element in line.items():
        elements_str += element.to_bmad() + "\n"

    line_str = f'{seq_name}: line = ('
    for name in line.names:
        if "$" in name:
            name = name.replace("$", "")
        line_str += name + ", \n"
    line_str = line_str[:-3]
    line_str += f") \nuse, {seq_name}"

    sequence = f"{beam_str} \n{elements_str} \n{line_str}"
    return sequence


