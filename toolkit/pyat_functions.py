import at
import numpy as np

def get_optics_pyat(ring, radiation=False):
    xy_step = 1.0e-10
    dp_step = 1.0e-9
    
    idx = get_indices(ring, [at.lattice.elements.Dipole, at.lattice.elements.Quadrupole, at.lattice.elements.Sextupole])
    
    if radiation:
        ring.radiation_on(quadrupole_pass='auto')
        ring.set_cavity_phase()
        ring.tapering(niter = 2, quadrupole=True, sextupole=True, XYStep=xy_step, DPStep=dp_step)
        l0,q,l = linopt6(ring,refpts=idx,get_chrom=True,
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
   


