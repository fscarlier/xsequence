from xsequence.lattice import Lattice
from xsequence.conversion_utils import conv_utils


"""
Imports from different sources
"""

# Import from cpymad instance
madx_lattice = conv_utils.create_cpymad_from_file("FCCee_h.seq", 120)
lat = Lattice.from_cpymad(madx_lattice, 'l000013')

#Import from pyat instance
pyat_lattice = conv_utils.create_pyat_from_file("FCCee_h.mat")
lat = Lattice.from_pyat(pyat_lattice)

#Import from madx sequence file (through cpymad)
lat = Lattice.from_madx_seqfile("FCCee_h.seq", 'l000013', 120)

"""
Basic data in Lattice()
"""

# Sequence representation of elements (without drifts)
lat.sequence
lat.sequence.names
lat.sequence.positions

# Can use lookup from slices with both index and name
lat.sequence['sd128.7']
lat.sequence['sd128.7':'qm8.2']
lat.sequence[90:120]


# Line representation of elements with explicit drifts
lat.line


"""
Manipulations
"""

# Get elements of specific type
quad_sext = lat.sequence.get_class(['Quadrupole', 'Sextupole'])

# Teapot slicing using default 1 slice
sliced_lat = lat.sliced

# Change slice number
for el in lat.sequence.get_class(['Quadrupole', 'Sextupole']):
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

"""
Xdeps dependencies
"""

from cpymad.madx import Madx

cpymad_ins = Madx(stdout=False)
cpymad_ins.call("lhc.seq")
cpymad_ins.call("optics.madx")
lat = Lattice.from_cpymad(cpymad_ins, seq_name='lhcb1', dependencies=True)

# lat.xdeps_manager.tasks
# print(lat.sequence['mqxa.1r1'].k1)
# lat.vref['kqx.r1'] = 0.01
# print(lat.sequence['mqxa.1r1'].k1)

for name, el in lat.sequence.find_elements('mqxa*').items():
    print(el.k1)

for el in lat.sequence.find_elements('mqxa*'):
    lat.sref[el].k1 = lat.sref[el].k1 + lat.vref['mqxa_knob']

for name, el in lat.sequence.find_elements('mqxa*').items():
    print(el.k1)

lat.vref['mqxa_knob'] = 0.015

for name, el in lat.sequence.find_elements('mqxa*').items():
    print(el.k1)

for el in lat.sequence.find_elements('mqxa*'):
    lat.sref[el].k1 = lat.vref['mqxa_knob'] + lat.vref['on_x1']

lat.vref['on_x1'] = 0.005

for name, el in lat.sequence.find_elements('mqxa*').items():
    print(el.k1)


