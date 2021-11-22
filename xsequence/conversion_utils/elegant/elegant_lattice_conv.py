"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import numpy as np
from xsequence.lattice_baseclasses import Line
from xsequence.elements import (
                    Marker, Drift, Collimator, Monitor, Placeholder, Instrument, 
                    SectorBend,  RectangularBend, Solenoid, ThinMultipole, Quadrupole, 
                    Sextupole, Octupole, RFCavity, HKicker, VKicker, TKicker, 
                    ThinMultipole, ThinSolenoid, ThinRFMultipole)



XSEQUENCE_TO_ELEGANT={
    Marker          : (lambda element: f"{element.name}: MARK;\n"),
    Drift           : (lambda element: f"{element.name}: EDRIFT,        L={element.length};\n"),
    Collimator      : (lambda element: f"{element.name}: RCOL,          L={element.length};\n"),
    Monitor         : (lambda element: f"{element.name}: MONI,          L={element.length};\n"),
    Placeholder     : (lambda element: f"{element.name}: MARK;\n"),
    Instrument      : (lambda element: f"{element.name}: MARK;\n"),
    SectorBend      : (lambda element: f"{element.name}: CSBEND,        L={element.length}, ANGLE={element.angle}, E1={element.e1}, E2={element.e2};\n"),
    RectangularBend : (lambda element: f"{element.name}: CSBEND,        L={element.length}, ANGLE={element.angle}, E1={element.e1}, E2={element.e2};\n"),
    Solenoid        : (lambda element: f"{element.name}: SOLE,          L={element.length}, KS={element.ks};\n"),
    Quadrupole      : (lambda element: f"{element.name}: KQUAD,         L={element.length}, K1={element.k1};\n"),
    Sextupole       : (lambda element: f"{element.name}: KSEXT,         L={element.length}, K2={element.k2};\n"),
    Octupole        : (lambda element: f"{element.name}: KOCT,          L={element.length}, K3={element.k3};\n"),
    RFCavity        : (lambda element: f"{element.name}: RFCA,          L={element.length}, VOLT={element.voltage}, PHASE={element.lag*180/np.pi}, FREQ={element.frequency};\n"),
    HKicker         : (lambda element: f"{element.name}: EHKICK,        L={element.length}, KICK={element.kick};\n"),
    VKicker         : (lambda element: f"{element.name}: EVKICK,        L={element.length}, KICK={element.kick};\n"),
    TKicker         : (lambda element: f"{element.name}: KICKER,        L={element.length}, HKICK={element.hkick}, VKICK={element.vkick};\n"),
    ThinMultipole   : (lambda element: ''.join([
                                       f"{element.name}.K{order}: MULT, L={element.length}, KNL={strength}, ORDER={order};\n" 
        for order, strength in enumerate(element.knl)
                                        ])),
    ThinSolenoid    : (lambda element: f"{element.name}: SOLE,          L={element.length}, KS={element.ks};\n"),
}

def to_elegant(seq_name: str, energy: float, line: Line) -> dict:

    lat=[]
    seq=f"{seq_name} : LINE=("
    for element in line:
        lat.append(XSEQUENCE_TO_ELEGANT[element.type()](element))
        seq=f"{seq}{element.name}, "
    seq=f"{seq})"
    return {'lattice': lat, 'sequence':seq, 'script': ele}

