from xsequence.lattice import Lattice
from cpymad.madx import Madx

mad=Madx(stdout=False)
mad.call("lhc.seq")
mad.call("optics.madx")
mad.command.beam(particle='proton')
seq_name = 'lhcb1'
mad.use(seq_name)

lat = Lattice.from_cpymad(mad, seq_name, dependencies=True)

print(lat.sequence['mcbcv.5r1.b1'])
lat.xdeps_manager.containers['v']['on_x1']=2
print(lat.sequence['mcbcv.5r1.b1'])



