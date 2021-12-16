"""
Module xsequence.lattice
------------------
:author: Felix Carlier (fcarlier@cern.ch)
This is a Python3 module containing base Lattice class to manipulate accelerator sequences.
"""

import math
import xdeps

from cpymad.madx import Madx
from collections import OrderedDict, defaultdict
from lark import Lark, Transformer, v_args

import xsequence.elements as xe
import xsequence.elements_dataclasses as xed
import xsequence.conversion_utils.cpymad.cpymad_properties as cpymad_properties

calc_grammar = """
    ?start: sum
        | NAME "=" sum      -> assign_var

    ?sum: product
        | sum "+" product   -> add
        | sum "-" product   -> sub

    ?product: power
        | product "*" atom  -> mul
        | product "/" atom  -> div

    ?power: atom
        | power "^" atom    -> pow

    ?atom: NUMBER           -> number
         | "-" atom         -> neg
         | "+" atom         -> pos
         | NAME             -> var
         | NAME "->" NAME   -> get
         | NAME "(" sum ("," sum)* ")" -> call
         | "(" sum ")"

    NAME: /[a-z_\.][a-z0-9_\.%]*/
    %import common.NUMBER
    %import common.WS_INLINE
    %ignore WS_INLINE
"""

@v_args(inline=True)
class XSequenceMadxEval(Transformer):
    from operator import add, sub, mul, truediv as div
    from operator import neg, pos, pow
    number = float

    def __init__(self,variables,functions,elements):
        self.variables = variables
        self.functions = functions
        self.elements  = elements
        self.eval=Lark(calc_grammar, parser='lalr',
                         transformer=self).parse

    def assign_var(self, name, value):
        self.variables[name] = value
        return value

    def call(self,name,*args):
        ff=getattr(self.functions,name)
        return ff(*args)

    def get(self,name,key):
        return getattr(self.elements.sequence[name[1]], key)

    def var(self, name):
        try:
            return self.variables[name.value]
        except KeyError:
            raise Exception("Variable not found: %s" % name)


def from_madx_seqfile(seq_file, seq_name, energy: float, particle_type: str = 'electron') -> Madx:
    """ Import lattice from MAD-X sequence file """
    madx = Madx()
    madx.option(echo=False, info=False, debug=False)
    madx.call(file=seq_file)
    madx.input('SET, FORMAT="25.20e";')
    return madx


def from_cpymad(madx: Madx, seq_name: str):
    variables=defaultdict(lambda :0)
    for name,par in madx.globals.cmdpar.items():
        variables[name]=par.value

    sequence_dict = OrderedDict()
    elements={}
    for elem in madx.sequence[seq_name].elements:
        elemdata={}
        for parname, par in elem.cmdpar.items():
            elemdata[parname]=par.value
        elements[elem.name]=elemdata
        sequence_dict[elem.name] = xe.convert_arbitrary_cpymad_element(elem) 

    for el in sequence_dict:
        if sequence_dict[el].position_data.reference_element:
            sequence_dict[el].position_data.reference = sequence_dict[sequence_dict[el].position_data.reference_element].position_data.position 

    return variables, sequence_dict 


def set_from_key(el, key, value):
    if key in xed.ElementID.INIT_PROPERTIES:
        setattr(el.id_data, key, value)
    elif key in xed.ElementParameterData.INIT_PROPERTIES:
        setattr(el.parameter_data, key, value)
    elif key in xed.ElementPosition.INIT_PROPERTIES:
        setattr(el.position_data, key, value)
    elif key in xed.ApertureData.INIT_PROPERTIES:
        setattr(el.aperture_data, key, value)
    elif key in xed.PyatData.INIT_PROPERTIES:
        setattr(el.pyat_data, key, value)
    else:
        setattr(el, key, value)


def from_cpymad_with_dependencies(madx: Madx, seq_name: str, dependencies: bool = False):
    variables, sequence_dict = from_cpymad(madx, seq_name)
    manager = xdeps.Manager()
    vref = manager.ref(variables,'v')
    mref = manager.ref(math,'m')
    sref = manager.ref(sequence_dict,'s')
    madeval = XSequenceMadxEval(vref,mref,sref).eval
    
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
                            sref[name]._set_from_key(parname, madeval(ee))
                else:
                    if parname in cpymad_properties.DIFF_ATTRIBUTE_MAP_CPYMAD_INVERTED:
                        parname = cpymad_properties.DIFF_ATTRIBUTE_MAP_CPYMAD_INVERTED[parname]
                    set_from_key(sref[name], parname, madeval(par.expr))

    return manager, vref, mref, sref, sequence_dict


def to_cpymad(seq_name, energy, sequence):
    madx = Madx()
    madx.option(echo=False, info=False, debug=False)
    seq_command = ''
    
    for name, element in sequence[1:-1].items():
        element.to_cpymad(madx)
        if len(element.position_data.reference_element) > 0:
            seq_command += f'{name}, at={element.position_data.location}, from={element.position_data.reference_element}  ;\n'
        else:
            seq_command += f'{name}, at={element.position_data.location} ;\n'

    madx.input(f'{seq_name}: sequence, refer=centre, l={sequence[sequence.names[-1]].position_data.end};')
    madx.input(seq_command)
    madx.input('endsequence;')
    madx.command.beam(particle='electron', energy=energy)
    return madx


