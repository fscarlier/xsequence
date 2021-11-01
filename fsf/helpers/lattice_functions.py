import xdeps, math
from collections import defaultdict, OrderedDict
import fsf.elements as xe


def from_cpymad(madx, seq_name):
    """
    Import lattice from cpymad sequence

    Args:
        madx: cpymad.madx Madx() instance
        seq_name: string, name of madx sequence
    """
    madx.use(seq_name)
    element_seq = list(map(xe.convert_arbitrary_cpymad_element, 
                            madx.sequence[seq_name].elements))
    
    element_seq = {el.name: xe.convert_arbitrary_cpymad_element(el) for el in madx.sequence[seq_name].elements}

    lat_seq = OrderedDict()
    elements={}
    lat_go = False
    for elem in madx.sequence[seq_name].elements:
        name = elem.name
        elemdata={}
        for parname, par in elem.cmdpar.items():
            elemdata[parname]=par.value
        elements[name]=elemdata
        if 'start' in name:
            lat_go = True
        if lat_go:
            lat_seq[name] = xe.convert_arbitrary_cpymad_element(elem) 


    variables=defaultdict(lambda :0)
    for name,par in madx.globals.cmdpar.items():
        variables[name]=par.value

    manager=xdeps.DepManager()
    vref=manager.ref(variables,'v')
    sref=manager.ref(element_seq,'s')
    fref=manager.ref(math,'f')
    madeval=xdeps.MadxEval(vref,fref,sref).eval

    for name,par in mad.globals.cmdpar.items():
        if par.expr is not None:
            vref[name]=madeval(par.expr)

    lat_go = False
    parlis = []
    for name,elem in mad.elements.items():
        for parname, par in elem.cmdpar.items():
            if par.expr is not None:
                if par.dtype==12: # handle lists
                    for ii,ee in enumerate(par.expr):
                        if ee is not None:
                            if parname in ['aper_vx', 'aper_vy']:
                                pass
                            else:
                                eref[name][parname][ii]=madeval(ee)
                else:
                    if parname not in parlis:
                        parlis.append(parname)
                    eref[name][parname]=madeval(par.expr)
                    if 'start' in name:
                        lat_go = True
                    if lat_go:
                        if parname == 'at':
                            lref[name].position_data.location = madeval(par.expr)
                        elif parname == 'l':
                            lref[name].length = madeval(par.expr)
                        
                        elif parname == 'kmax':
                            try:
                                lref[name].strength_data.kmax = madeval(par.expr)
                            except AttributeError:
                                lref[name].kick_data.kmax = madeval(par.expr)
                        elif parname == 'kmin':
                            try:
                                lref[name].strength_data.kmin = madeval(par.expr)
                            except AttributeError:
                                lref[name].kick_data.kmin = madeval(par.expr)
                        # elif parname == 'calib':
                        #     lref[name]. = madeval(par.expr)
                        elif parname == 'polarity':
                            lref[name].strength_data.polarity = madeval(par.expr)
                        elif parname == 'tilt':
                            lref[name].position_data.tilt = madeval(par.expr)
                        elif parname == 'k0':
                            lref[name].bend_data.k0 = madeval(par.expr)
                        elif parname == 'k1':
                            lref[name].strength_data.k1 = madeval(par.expr)
                        elif parname == 'k1s':
                            lref[name].strength_data.k1s = madeval(par.expr)
                        elif parname == 'k2':
                            lref[name].strength_data.k2 = madeval(par.expr)
                        elif parname == 'k2s':
                            lref[name].strength_data.k2s = madeval(par.expr)
                        elif parname == 'k3':
                            lref[name].strength_data.k3 = madeval(par.expr)
                        elif parname == 'angle':
                            lref[name].bend_data.angle = madeval(par.expr)
                        elif parname == 'kick':
                            lref[name].kick_data.kick = madeval(par.expr)
                        elif parname == 'hkick':
                            lref[name].kick_data.hkick = madeval(par.expr)
                        elif parname == 'vkick':
                            lref[name].kick_data.vkick = madeval(par.expr)
                        elif parname == 'volt':
                            lref[name].rf_data.voltage = madeval(par.expr)
                        elif parname == 'lag':
                            lref[name].rf_data.lag = madeval(par.expr)
                        elif parname == 'slot_id':
                            lref[name].id_data.slot_id = madeval(par.expr)
                        elif parname == 'assembly_id':
                            lref[name].id_data.assembly_id = madeval(par.expr)

    timeit()
    for el in lat_seq:
        if lat_seq[el].position_data.reference_element:
            lat_seq[el].position_data.reference = lat_seq[lat_seq[el].position_data.reference_element].position_data.position 

    timeit()

    lhcb1_seq = []
    lhcb2_seq = []
    lhcb1 = True
    lhcb2 = False
    for elname in lat_seq:
        if lhcb1:
            lhcb1_seq.append(lat_seq[elname])   
            if 'lhcb1$end' in elname:
                lhcb1 = False
        if 'lhcb2$start' in elname:
            lhcb2 = True
        if lhcb2:
            lhcb2_seq.append(lat_seq[elname])   
        
    timeit()

    lhcb1_seq[-1].position_data.location = lhcb1_seq[-2].position_data.end
    lhcb2_seq[-1].position_data.location = lhcb2_seq[-2].position_data.end
    print(lhcb1_seq[-1])
    print(lhcb2_seq[0])


    lhcb1 = Lattice('lhcb1', lhcb1_seq, key='sequence', global_variables=vref) 
    lhcb2 = Lattice('lhcb2', lhcb2_seq, key='sequence', global_variables=vref) 
    timeit()

    print("""
    Still need to implement:
    - calib
    - kick
    - vkick
    - hkick
    - kmax, kmin for kickers
    """)
    timeit()


    import time
    start=time.time()
    print(elements['mcbcv.5r1.b2']['kick'])
    vref['on_x1']=2
    print(elements['mcbcv.5r1.b2']['kick'])
    print(time.time()-start)



