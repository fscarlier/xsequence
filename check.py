import conversion_functions as cf
import matplotlib.pyplot as plt
from fcc_plots import fcc_axes

md = cf.create_cpymad_from_file('lattice.seq', 120)
seq = cf.import_lattice_from_cpymad(md)
md_seq = cf.create_cpymad_from_lattice(seq)

md_seq.use('l000013')
twiss_seq = md_seq.twiss(file='md_seq.twiss', sequence='l000013')
md.use('l000013')
twiss = md.twiss(file='md.twiss', sequence='l000013')

mde = md.sequence['l000013'].elements
mdes = md_seq.sequence['l000013'].elements


fig1, ax1 = fcc_axes()
ax1.plot(twiss.s, twiss.x - twiss_seq.x, label=r'x')
ax1.plot(twiss.s, twiss.y - twiss_seq.y, label=r'y')
ax1.set_ylabel(r'Orbit [m]')
ax1.legend(loc='upper right')

fig2, ax2 = fcc_axes()
ax2.plot(twiss.s, 100*(twiss.betx - twiss_seq.betx)/twiss.betx, label=r'cpymad vs. cpymad*')
ax2.set_ylabel(r'$\Delta\beta_x/\beta_x \quad [\%]$')
ax2.legend(loc='upper right')

fig3, ax3 = fcc_axes()
ax3.plot(twiss.s, 100*(twiss.bety - twiss_seq.bety)/twiss.bety, label=r'cpymad vs. cpymad*')
ax3.set_ylabel(r'$\Delta\beta_y/\beta_y \quad [\%]$')
ax3.legend(loc='upper right')

fig4, ax4 = fcc_axes()
ax4.plot(twiss.s, (twiss.dx - twiss_seq.dx)*1e3, label=r'cpymad vs. cpymad*')
ax4.set_ylabel(r'$\Delta D_x \quad [10^{-3}]$')
ax4.legend(loc='upper right')

fig5, ax5 = fcc_axes()
ax5.plot(twiss.s, (twiss.dy - twiss_seq.dy)*1e3, label=r'cpymad vs. cpymad*')
ax5.set_ylabel(r'$\Delta D_y \quad [10^{-3}]$')
ax5.legend(loc='upper right')

fig6, ax6 = fcc_axes()
ax6.plot(twiss.s, (twiss.alfx - twiss_seq.alfx)/twiss.alfx, label=r'cpymad vs. cpymad*')
ax6.set_ylabel(r'$\alpha_x$')
ax6.legend(loc='upper right')

fig7, ax7 = fcc_axes()
ax7.plot(twiss.s, (twiss.alfy - twiss_seq.alfy)/twiss.alfy, label=r'cpymad vs. cpymad*')
ax7.set_ylabel(r'$\alpha_y$')
ax7.legend(loc='upper right')


plt.show()


