"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

def to_bmad(lattice: Lattice) -> str:
    assert lattice.beam.energy
    assert lattice.beam.particle

    beam_str = f"beam, energy = {lattice.beam.energy} \nparameter[particle] = {lattice.beam.particle}\n"
    elements_str = ""
    
    for _, element in lattice.line.items():
        elements_str += element.to_bmad() + "\n"

    line_str = f'{lattice.name}: line = ('
    for name in lattice.line.names:
        if "$" in name:
            name = name.replace("$", "")
        line_str += name + ", \n"
    line_str = line_str[:-3]
    line_str += f") \nuse, {lattice.name}"

    sequence = f"{beam_str} \n{elements_str} \n{line_str}"
    return sequence


