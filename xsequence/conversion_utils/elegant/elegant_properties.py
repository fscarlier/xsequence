import numpy as np


CONVERT_ELEMENT_DICT={
    'marker'          : (lambda element: f"{element['name']}: MARK"),
    'drift'           : (lambda element: f"{element['name']}: EDRIFT,        L={element['length']}"),
    'collimator'      : (lambda element: f"{element['name']}: RCOL,          L={element['length']}"),
    'monitor'         : (lambda element: f"{element['name']}: MONI,          L={element['length']}"),
    'placeholder'     : (lambda element: f"{element['name']}: MARK"),
    'instrument'      : (lambda element: f"{element['name']}: MARK"),
    'sectorbend'      : (lambda element: f"{element['name']}: CSBEND,        L={element['length']}, ANGLE={element['angle']}, E1={element['e1']}, E2={element['e2']}"),
    'rectangularbend' : (lambda element: f"{element['name']}: CSBEND,        L={element['length']}, ANGLE={element['angle']}, E1={element['e1']}, E2={element['e2']}"),
    'solenoid'        : (lambda element: f"{element['name']}: SOLE,          L={element['length']}, KS={element['ks']}"),
    'quadrupole'      : (lambda element: f"{element['name']}: KQUAD,         L={element['length']}, K1={element['k1']}"),
    'sextupole'       : (lambda element: f"{element['name']}: KSEXT,         L={element['length']}, K2={element['k2']}"),
    'octupole'        : (lambda element: f"{element['name']}: KOCT,          L={element['length']}, K3={element['k3']}"),
    'rfcavity'        : (lambda element: f"{element['name']}: RFCA,          L={element['length']}, VOLT={element['voltage']*10**6}, PHASE={element['lag']*180/np.pi}, FREQ={element['frequency']*10**6}"),
    'hkicker'         : (lambda element: f"{element['name']}: EHKICK,        L={element['length']}, KICK={element['kick']}"),
    'vkicker'         : (lambda element: f"{element['name']}: EVKICK,        L={element['length']}, KICK={element['kick'] }"),
    'tkicker'         : (lambda element: f"{element['name']}: KICKER,        L={element['length']}, HKICK={element['hkick']}, VKICK={element['vkick']}"),
    'thinmultipole'   : (lambda element: ''.join([
                                       f"{element['name']}.K{order}: MULT, L={element['length']}, KNL={strength}, ORDER={order}\n" 
        for order, strength in enumerate(element['knl'])
                                        ])),
    'thinsolenoid'    : (lambda element: f"{element['name']}: SOLE,          L={element['length']}, KS={element['ks']}"),
}