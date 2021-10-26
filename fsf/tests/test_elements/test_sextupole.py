import fsf.elements as xe
from pytest import mark
from cpymad.madx import Madx

@mark.parametrize('name,    l',
                 [( 'q1', 1.2),
                  ( 'q2', 0.2)])
def test_sextupole_length(name, l):
    q = xe.Sextupole(name, length=l)
    assert q.name == name
    assert q.position_data.length == l
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Sextupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    pyat_sext = q.to_pyat()
    assert pyat_sext.FamName == q.name
    assert pyat_sext.Length == q.length
    q_pyat = xe.Sextupole.from_pyat(pyat_sext)
    assert q == q_pyat


@mark.parametrize('name,    l,   k2',
                 [( 'q1', 1.2, -1.3),
                  ( 'q2', 0.2,  1.1)])
def test_sextupole_length_k2(name, l, k2):
    q = xe.Sextupole(name, length=l, k2=k2)
    assert q.name == name
    assert q.length == l
    assert q.strength_data.k2 == k2
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Sextupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    pyat_sext = q.to_pyat()
    assert pyat_sext.FamName == q.name
    assert pyat_sext.Length == q.length
    assert pyat_sext.H*2. == q.k2
    q_pyat = xe.Sextupole.from_pyat(pyat_sext)
    assert q == q_pyat


@mark.parametrize('name,    l,  k2s',
                 [( 'q1', 1.2, -1.3),
                  ( 'q2', 0.2,  1.1)])
def test_sextupole_length_k2s(name, l, k2s):
    q = xe.Sextupole(name, length=l, k2s=k2s)
    assert q.name == name
    assert q.length == l
    assert q.strength_data.k2s == k2s
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Sextupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    pyat_sext = q.to_pyat()
    assert pyat_sext.FamName == q.name
    assert pyat_sext.Length == q.length
    q_pyat = xe.Sextupole.from_pyat(pyat_sext)
    assert q == q_pyat


@mark.parametrize('name,    l,   k2,  k2s',
                 [( 'q1', 1.2, -1.3,  1.3),
                  ( 'q2', 1.2,  1.3, -1.3),
                  ( 'q3', 1.2, -1.1, -1.3),
                  ( 'q4', 0.2,  1.1,  1.3)])
def test_sextupole_length_k2_k2s(name, l, k2, k2s):
    q = xe.Sextupole(name, length=l, k2=k2, k2s=k2s)
    assert q.name == name
    assert q.length == l
    assert q.strength_data.k2 == k2
    assert q.strength_data.k2s == k2s
    
    #CPYMAD
    md = Madx()
    q_conv = xe.Sextupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv
    
    #PYAT
    pyat_sext = q.to_pyat()
    assert pyat_sext.FamName == q.name
    assert pyat_sext.Length == q.length
    assert pyat_sext.H*2. == q.k2
    q_pyat = xe.Sextupole.from_pyat(pyat_sext)
    assert q == q_pyat


