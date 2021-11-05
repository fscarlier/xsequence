from xsequence.lattice import Lattice
from conversion_utils import conv_utils


"""
Imports from different sources
"""

# Import from cpymad instance
madx_lattice = conv_utils.create_cpymad_from_file("fcc-ee_h.seq", 120)
lat = Lattice.from_cpymad(madx_lattice, 'l000013')

#Import from pyat instance
pyat_lattice = conv_utils.create_pyat_from_file("fcch_norad.mat")
lat = Lattice.from_pyat(pyat_lattice)

#Import from madx sequence file (through cpymad)
lat = Lattice.from_madx_seqfile("fcc-ee_h.seq", 'l000013', 120)

"""
Basic data in Lattice()
"""

# Sequence representation of elements (without drifts)
lat.sequence

# Line representation of elements with explicit drifts
lat.line


"""
Manipulations
"""

# Get elements of specific type
quad_sext = lat.get_class(['Quadrupole', 'Sextupole'])

# Find element by name
elem = lat.get_element('bg6.1')

# Select element ranges using positions or elements
section = lat.get_range_s(1100, 1200)
section = lat.get_range_elements('qg7.1', 'qd3.4')

# Obtain s positions of Lattice
s_positions = lat.get_s_positions()

# Teapot slicing using default 1 slice
sliced_lat = lat.sliced

# Change slice number
quad_sext = lat.get_class(['Quadrupole', 'Sextupole'])
for el in quad_sext:
    el.int_steps = 5

sliced_lat = lat.sliced

"""
Quick optics checks
"""
df_mad = lat.optics(engine='madx', drop_drifts=True)
df_pyat = lat.optics(engine='pyat', drop_drifts=True)

"""
Exports to different sources
"""

madx = lat.to_cpymad()
pyat = lat.to_pyat()
line = lat.to_xline()
