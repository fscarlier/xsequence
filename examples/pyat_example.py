from xsequence.lattice import Lattice
from xsequence.conversion_utils import conv_utils

lat = Lattice.from_madx_seqfile("FCCee_h.seq", 'l000013', energy=120)
plat = lat.to_pyat()

import at
import matplotlib.pyplot as plt

plat.radiation_off()
l0,q,qp,l = at.linopt(plat,refpts=range(len(plat)))
ax1,=plt.plot(l.s_pos,l.beta[:,0])
ax2,=plt.plot(l.s_pos,l.beta[:,1])
plt.show()

def update_twiss(plat,elements):
    plat.radiation_off()
    l0,q,qp,l = at.linopt(plat,refpts=range(len(plat)))
    ax1.set_ydata(l.beta[:,0])
    ax2.set_ydata(l.beta[:,1])

import xdeps

plat.e=dict( (el.FamName,el) for el in plat)
plat.v = xdeps.utils.AttrDict()

manager = xdeps.Manager()
pref=manager.ref(plat,'plat')

pref.update_twiss=update_twiss
pref.up=pref.update_twiss(pref,pref.e)

pref.v.dk=0
pref.e['qc1l1.1'].K=-0.24949831119187935*(1+pref.v.dk)

pref.v.dk=plat.v.dk+0.001

# manager.to_pydot(list(manager.tasks))

