import fsf.elements as xe
import fsf.elements_dataclasses as xed
from pytest import mark
from cpymad.madx import Madx


@mark.parametrize('name,    l',
                 [( 'q1', 1.2),
                  ( 'q2', 0.2)])
def test_octupole_length(name, l):
    q = xe.Octupole(name, length=l)
    assert q.name == name
    assert q.position_data.length == l
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Octupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    q = xe.Octupole(name, length=l, pyat_data=xed.PyatData(NumIntSteps=10, PassMethod='StrMPoleSymplectic4Pass'))
    pyat_oct = q.to_pyat()
    assert pyat_oct.FamName == q.name
    assert pyat_oct.Length == q.length
    q_pyat = xe.Octupole.from_pyat(pyat_oct)
    assert q == q_pyat



@mark.parametrize('name,    l,   k3',
                 [( 'q1', 1.2, -1.3),
                  ( 'q2', 0.2,  1.1)])
def test_octupole_length_k3(name, l, k3):
    q = xe.Octupole(name, length=l, k3=k3)
    assert q.name == name
    assert q.length == l
    assert q.k3 == k3
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Octupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    q = xe.Octupole(name, length=l, k3=k3, pyat_data=xed.PyatData(NumIntSteps=10, PassMethod='StrMPoleSymplectic4Pass'))
    pyat_oct = q.to_pyat()
    assert pyat_oct.FamName == q.name
    assert pyat_oct.Length == q.length
    q_pyat = xe.Octupole.from_pyat(pyat_oct)
    assert q == q_pyat



@mark.parametrize('name,    l,  k3s',
                 [( 'q1', 1.2, -1.3),
                  ( 'q2', 0.2,  1.1)])
def test_octupole_length_k3s(name, l, k3s):
    q = xe.Octupole(name, length=l, k3s=k3s)
    assert q.name == name
    assert q.length == l
    assert q.k3s == k3s
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Octupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    q = xe.Octupole(name, length=l, k3s=k3s, pyat_data=xed.PyatData(NumIntSteps=10, PassMethod='StrMPoleSymplectic4Pass'))
    pyat_oct = q.to_pyat()
    assert pyat_oct.FamName == q.name
    assert pyat_oct.Length == q.length
    assert pyat_oct.PolynomA[3]*6. == q.k3s
    q_pyat = xe.Octupole.from_pyat(pyat_oct)
    assert q == q_pyat



@mark.parametrize('name,    l,   k3,  k3s',
                 [( 'q1', 1.2, -1.3,  1.3),
                  ( 'q2', 1.2,  1.3, -1.3),
                  ( 'q3', 1.2, -1.1, -1.3),
                  ( 'q4', 0.2,  1.1,  1.3)])
def test_octupole_length_k3_k3s(name, l, k3, k3s):
    q = xe.Octupole(name, length=l, k3=k3, k3s=k3s)
    assert q.name == name
    assert q.length == l
    assert q.k3 == k3
    assert q.k3s == k3s
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Octupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    q = xe.Octupole(name, length=l, k3=k3, k3s=k3s, pyat_data=xed.PyatData(NumIntSteps=10, PassMethod='StrMPoleSymplectic4Pass'))
    pyat_oct = q.to_pyat()
    assert pyat_oct.FamName == q.name
    assert pyat_oct.Length == q.length
    q_pyat = xe.Octupole.from_pyat(pyat_oct)
    assert q == q_pyat



