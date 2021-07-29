import conversion_functions as cf
import matplotlib.pyplot as plt
from fcc_plots import fcc_axes
import at
import numpy as np
import pandas as pd
from pyat_functions import get_optics_pyat, get_indices


def get_lattices():
    md = cf.create_cpymad_from_file('FCCee_h_217_nosol_3.seq', 120)
    seq = cf.import_lattice_from_cpymad(md)
    ring = cf.create_pyat_from_lattice(seq)

    ring_mat = at.load.matfile.load_mat('./fcch_norad.mat', key='ring')
    ring_mat = at.Lattice(ring_mat)
    return ring, ring_mat


def to_csv(file_name, ring, spos, l):
    names = []
    idx = get_indices(ring, [at.lattice.elements.Dipole, at.lattice.elements.Quadrupole, at.lattice.elements.Sextupole])
    for i in idx:
        names.append(ring[i].FamName.upper())

    df = pd.DataFrame({'NAME':names, 'S':spos, 'BETX':l.beta[:,0], 'BETY':l.beta[:,1], 
                       'DX':l.dispersion[:,0], 'DY':l.dispersion[:,1], 
                       'X':l.closed_orbit[:,0], 'PX':l.closed_orbit[:,1], 
                       'Y':l.closed_orbit[:,2], 'PY':l.closed_orbit[:,3], 
                       'DELTA':l.closed_orbit[:,4], 'CT':l.closed_orbit[:,5]}) 
    df.to_csv(file_name)


def compare_elements(ring, ring_mat):
    for i in range(20):
        print(ring[i+1])
        print(ring_mat[i])
        print("-----------------------------")


def plot_optics(spos, l, sposc, lc):
    fig1, ax1 = fcc_axes()
    ax1.plot(spos, sposc-spos)

    fig2, ax2 = fcc_axes()
    ax2.plot(spos, (lc.beta[:,0] - l.beta[:,0])/l.beta[:,0])
    ax2.set_ylabel('beta x (conv - ref)/ref')

    fig3, ax3 = fcc_axes()
    ax3.plot(spos, (lc.beta[:,1] - l.beta[:,1])/l.beta[:,1])
    ax3.set_ylabel('beta y (conv - ref)/ref')

    fig4, ax4 = fcc_axes()
    ax4.plot(spos,lc.dispersion[:,0] - l.dispersion[:,0])
    ax4.set_ylabel('dispersion x (conv - ref)')

    fig5, ax5 = fcc_axes()
    ax5.plot(spos, lc.closed_orbit[:,0] - l.closed_orbit[:,0])
    ax5.set_ylabel('orbit x (conv - ref)')

    fig6, ax6 = fcc_axes()
    ax6.plot(spos, lc.closed_orbit[:,2] - l.closed_orbit[:,2])
    ax6.set_ylabel('orbit y (conv - ref)')

    fig7, ax7 = fcc_axes()
    ax7.plot(spos, lc.closed_orbit[:,4] - l.closed_orbit[:,4])
    ax7.set_ylabel('orbit z (conv - ref)')

    fig8, ax8 = fcc_axes()
    ax8.plot(spos, lc.closed_orbit[:,5] - l.closed_orbit[:,5])
    ax8.set_ylabel('orbit pz (conv - ref)')
    plt.show()


if __name__ == '__main__':
    ring, ring_mat = get_lattices()

    compare_elements(ring, ring_mat)
    optics_ring, s_ring = get_optics_pyat(ring)
    optics_mat, s_mat = get_optics_pyat(ring_mat)
    print(len(optics_ring), len(optics_mat))
    print(len(s_ring), len(s_mat))
    to_csv('/home/fcarlier/personal/cern-gitlab/data/pyat/norad_notap/results.csv', ring, s_ring, optics_ring)
    
    # plot_optics(s_ring, optics_ring, s_mat, optics_mat)
