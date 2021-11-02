import time, math, xdeps
import fsf.elements as xe 
from fsf.lattice import Lattice
from collections import OrderedDict, defaultdict
from cpymad.madx import Madx

t0  = time.time()

def timeit(message=''):
    if hasattr(timeit,'start'):
        newstart=time.time()
        print(f"{message}: {newstart-timeit.start:13.9f} sec")
    timeit.start=time.time()

timeit()

timeit(message='start')

madx=Madx(stdout=False)
madx.call("lhc.seq")
madx.call("optics.madx")
seq_name = 'lhcb1'

timeit(message='madx creation')

variables=defaultdict(lambda :0)

for name,par in madx.globals.cmdpar.items():
    variables[name]=par.value

timeit(message='variables creation')

sequence_dict = OrderedDict()
elements={}
for elem in madx.sequence[seq_name].elements:
    elemdata={}
    for parname, par in elem.cmdpar.items():
        elemdata[parname]=par.value
    elements[elem.name]=elemdata
    sequence_dict[elem.name] = xe.convert_arbitrary_cpymad_element(elem) 

timeit(message='elements dicts creation')

manager=xdeps.DepManager()
vref=manager.ref(variables,'variables')
eref=manager.ref(elements,'elements')
lref=manager.ref(sequence_dict,'lattice')
mref=manager.ref(math,'math')
madeval=xdeps.MadxEval(vref,mref,eref).eval

timeit(message='xdeps manager and eval')

for name,par in madx.globals.cmdpar.items():
    if par.expr is not None:
        vref[name]=madeval(par.expr)

for elem in madx.sequence[seq_name].elements:
    name = elem.name
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

timeit(message='setting deps')

for el in sequence_dict:
    if sequence_dict[el].position_data.reference_element:
        sequence_dict[el].position_data.reference = sequence_dict[sequence_dict[el].position_data.reference_element].position_data.position 

timeit(message='setting reference positions')

# lhcb1_seq = []
# lhcb2_seq = []
# lhcb1 = True
# lhcb2 = False
# for elname in sequence_dict:
#     if lhcb1:
#         lhcb1_seq.append(sequence_dict[elname])   
#         if 'lhcb1$end' in elname:
#             lhcb1 = False
#     if 'lhcb2$start' in elname:
#         lhcb2 = True
#     if lhcb2:
#         lhcb2_seq.append(sequence_dict[elname])   
#     
# timeit()



lhcb1 = Lattice('lhcb1', sequence_dict, key='sequence', xdeps_manager=manager) 
timeit(message='Create Lattice instance')

timeit("""
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
vref['on_x1']=2
timeit(time.time()-start)


print(f'total time: {time.time() - t0}')

