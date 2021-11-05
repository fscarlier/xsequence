from rich.console import Console
from rich.theme import Theme

from xsequence.lattice_baseclasses import Sequence, Line

custom_theme = Theme({"success": "green", "error":"red1", "warning":"orange3"})
console = Console(theme=custom_theme)


def compare_lattice_name(lat1, lat2):
    console.print("")
    console.print("")
    console.print(f"-- Comparing global      ")
    console.print("")
    console.print(f"---- Checking lattice names")
    if lat1.name == lat2.name:
        console.print(f"Identical Lattice name: {lat1.name}", style="success")
        return True
    else:
        console.print(f"Different Lattice names", style="error")
        console.print(f"        {lat1.name}  <-->  {lat2.name}"  )
        return False


def compare_sequence_lengths(sequence_1: Sequence, sequence_2: Sequence):
    console.print("")
    console.print(f"---- Checking sequence lengths")
    if len(sequence_1.positions) == len(sequence_2.positions):
        console.print(f"Identical sequence lengths: {len(sequence_1)}", style="success")
        return True
    else:
        console.print(f"Different sequence lengths: {len(sequence_1)}, {len(sequence_2)}", style="error")
        return False


def compare_elements(sequence_1: Sequence, sequence_2: Sequence, ignore_attributes = []):
    console.print("")
    console.print("")
    console.print(f"-- Comparing elements     ")
    console.print("")
    console.print(f"---- Checking element names")
    
    no_error = True
    for el in sequence_1:
        if el not in sequence_2:
            console.print(f"Element '{el}' is not in Lattice 2", style="error")
            no_error = False
    for el in sequence_2:
        if el not in sequence_1:
            console.print(f"Element '{el}' is not in Lattice 1", style="error")
            no_error = False
    if no_error:
        console.print(f"All elements present in other lattice", style="success")
    
    console.print("")
    console.print("")
    
    console.print(f"---- Checking element attributes")
    
    for el in sequence_1:
        if el not in sequence_2:
            pass
        else:
            if sequence_1[el] != sequence_2[el]:
                console.print(f"Element '{el}' not equal between lattices", style="error")
                seq1_dict = sequence_1[el].get_dict()
                seq2_dict = sequence_2[el].get_dict()
                for k in seq1_dict:
                    if k not in ignore_attributes:
                        if seq1_dict[k] != seq2_dict[k]:
                            console.print(f"    Attribute '{k}' is not equal", style="warning")
                            console.print(f"        {seq1_dict[k]}  <-->  {seq2_dict[k]}"  )
                no_error = False
    if no_error:
        console.print(f"All elements in sequence are identical", style="success")
        return True
    else:
        return False


def compare_lattices(lattice_1, lattice_2, ignore_attributes=[], debug=False):
    
    no_errors = True
    no_errors *= compare_lattice_name(lattice_1, lattice_2)
    no_errors *= compare_sequence_lengths(lattice_1.sequence, lattice_2.sequence)
    no_errors *= compare_elements(lattice_1.sequence, lattice_2.sequence, ignore_attributes=ignore_attributes)
    return no_errors