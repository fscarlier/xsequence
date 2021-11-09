# xdeps dependencies

from cpymad.madx import Madx
cpymad_ins = Madx(stdout=False)
cpymad_ins.call("lhc.seq")
cpymad_ins.call("optics.madx")

lat = Lattice.from_cpymad(cpymad_ins, seq_name=”lhcb1”, 
    dependencies=True)

print(lat.sequence[”mqxa.1r1”].k1)
lat.vref[“kqx.r1”] = 0.01
print(lat.sequence[“mqxa.1r1”].k1)

for el in lat.sequence.find_elements(“mqxa*”):
    lat.sref[el].k1 = lat.vref[“mqxa_knob”]

for name, el in lat.sequence.find_elements(“mqxa*”).items():
    print(el.k1)

lat.vref[“mqxa_knob”] = 0.015

for name, el in lat.sequence.find_elements(“mqxa*”).items():
    print(el.k1)

