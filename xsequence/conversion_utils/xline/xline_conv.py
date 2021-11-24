"""
Module conversion_utils.xline_conv
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing functions to convert elements from and to xline.
"""

import xtrack as xl


def marker_to_xline(element):
    kwargs = {'length':0} 
    return xl.Drift(**kwargs)


def drift_to_xline(element):
    kwargs = {'length':element.length} 
    return xl.Drift(**kwargs)


def thin_multipole_to_xline(element):
    kwargs = {'knl':element.knl, 
              'ksl':element.ksl}
    return xl.Multipole(**kwargs)


def rfcavity_to_xline(element):
    kwargs = {'voltage':element.voltage*1e6, 
              'frequency':element.frequency*1e6, 
              'lag':element.lag}
    return xl.Cavity(**kwargs)


def dipole_edge_to_xline(element):
    kwargs = {'h':element.h, 
              'e1':element.edge_angle} 
    return xl.DipoleEdge(**kwargs)


def convert_element_to_xline(xsequence_element):
    return TO_XLINE_CONV[xsequence_element.__class__.__name__](xsequence_element)


TO_XLINE_CONV = {'Marker':  marker_to_xline, 
                 'Drift':  drift_to_xline, 
                 'ThinMultipole':  thin_multipole_to_xline, 
                 'RFCavity': rfcavity_to_xline,
                 'DipoleEdge': dipole_edge_to_xline} 


