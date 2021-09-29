import at
import numpy as np
import pandas as pd


def pyat_optics_to_pandas_df(ring, lin):
    df = pd.DataFrame()
    df['name'] = [ring[i].FamName for i in lin['idx']]
    df['keyword'] = [ring[i].__class__.__name__.lower() for i in lin['idx']]
    df['s'] = lin['s_pos']
    df['betx'] = lin['beta'][:,0]
    df['bety'] = lin['beta'][:,1]
    df['alfx'] = lin['alpha'][:,0]
    df['alfy'] = lin['alpha'][:,1]
    df['mux'] = lin['mu'][:,0]
    df['muy'] = lin['mu'][:,1]
    df['dx'] = lin['dispersion'][:,0]
    df['dy'] = lin['dispersion'][:,1]
    df['x'] = lin['closed_orbit'][:,0]
    df['px'] = lin['closed_orbit'][:,1]
    df['y'] = lin['closed_orbit'][:,2]
    df['py'] = lin['closed_orbit'][:,3]
    df['delta'] = lin['closed_orbit'][:,4]
    df['ct'] = lin['closed_orbit'][:,5]
    return df

def calc_optics_pyat(ring, radiation=False, xy_step = 1.0e-10, dp_step = 1.0e-9):


    dipoles = at.get_refpts(ring, at.lattice.elements.Dipole)
    multipoles = at.get_refpts(ring, at.lattice.elements.Multipole)
    at.set_value_refpts(ring, dipoles, 'NumIntStep',40)
    at.set_value_refpts(ring, multipoles, 'NumIntStep',40)


    if radiation:
        ring.radiation_on(quadrupole_pass='auto')
        ring.set_cavity_phase()
        ring.tapering(niter = 2, quadrupole=True, sextupole=True, XYStep=xy_step, DPStep=dp_step)
        l0,q,l = at.linopt6(ring,refpts=range(len(ring)),get_chrom=True,
                            coupled=False, XYStep=xy_step, DPStep=dp_step)
    else: 
        ring.radiation_off()
        l0,q,qp,l = at.linopt(ring,refpts=range(len(ring)),get_chrom=True,
                            coupled=False, XYStep=xy_step, DPStep=dp_step)
    return l 


def get_optics_pyat(ring, radiation=False, xy_step = 1.0e-10, dp_step = 1.0e-9):
    idx = get_indices(ring, [at.lattice.elements.Dipole, at.lattice.elements.Quadrupole, at.lattice.elements.Sextupole])
    
    if radiation:
        ring.radiation_on(quadrupole_pass='auto')
        ring.set_cavity_phase()
        ring.tapering(niter = 2, quadrupole=True, sextupole=True, XYStep=xy_step, DPStep=dp_step)
        l0,q,l = at.linopt6(ring,refpts=idx,get_chrom=True,
                            coupled=False, XYStep=xy_step, DPStep=dp_step)
    else: 
        ring.radiation_off()
        l0,q,qp,l = at.linopt(ring,refpts=idx,get_chrom=True,
                            coupled=False, XYStep=xy_step, DPStep=dp_step)

    spos = ring.get_s_pos(idx)
    return l, spos 

    

def get_indices(lat, element_types):
    indices = []
    for el_type in element_types:
        idx = at.get_refpts(lat, el_type)
        indices.append(idx)
    indices = np.sort(np.concatenate(indices))
    return indices
   


