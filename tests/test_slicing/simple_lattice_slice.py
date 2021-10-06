from fsf.lattice import Lattice
from fsf.elements import Marker, Drift, Sbend, Rbend, Quadrupole, Sextupole


# Sbends and Rbends in line representation
sb1 = Sbend('sb1', length=1.0, angle=0.2)
sb2 = Sbend('sb2', length=1.0, angle=0.4)
rb1 = sb1.convert_to_rbend()
rb2 = sb2.convert_to_rbend()

ms = Marker('start')
me = Marker('end')

lat = Lattice('lat', [ms, sb1, d1, sb2, d2, me], key='line')
for q in lat.get_class('Sbend'):
    q.int_steps = 3

lat_sl = lat.slice_lattice()
thin_lattice = Lattice('lat', lat_sl, key='sequence')


# Sbends and Rbends in sequence representation
sb1 = Sbend('sb1', length=1.0, angle=0.2, position=1)
sb2 = Sbend('sb2', length=1.0, angle=0.4, position=3)
rb1 = sb1.convert_to_rbend()
rb2 = sb2.convert_to_rbend()

ms = Marker('start', position=0)
me = Marker('end', position=5)

lat = Lattice('lat', [ms, sb1, sb2, me], key='sequence')
for q in lat.get_class('Sbend'):
    q.int_steps = 3

lat_sl = lat.slice_lattice()
thin_lattice = Lattice('lat', lat_sl, key='sequence')


# Quadrupoles and Drifts in line representation
q1 = Quadrupole('q1', length=1.0, k1=4.0)
q2 = Quadrupole('q2', length=1.0, k1=4.0)
q3 = Quadrupole('q3', length=1.0, k1=4.0)
q4 = Quadrupole('q4', length=1.0, k1=4.0)
q5 = Quadrupole('q5', length=1.0, k1=4.0)

d1 = Drift('d1', length=2.0)
d2 = Drift('d2', length=2.0)
d3 = Drift('d3', length=2.0)
d4 = Drift('d4', length=2.0)
d5 = Drift('d5', length=2.0)

ms = Marker('start')
me = Marker('end')

lat = Lattice('lat', [ms, q1, d1, q2, d2, q3, d3, q4, d4, q5, d5, me], key='line')
for q in lat.get_class('Quadrupole'):
    q.int_steps = 3

lat_sl = lat.slice_lattice()
thin_lattice = Lattice('lat', lat_sl, key='sequence')

