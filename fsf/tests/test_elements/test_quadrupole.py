import fsf.elements as xe
from pytest import mark
from cpymad.madx import Madx

@mark.parametrize('name,    l',
                 [( 'q1', 1.2),
                  ( 'q2', 0.2)])
def test_quadrupole_length(name, l):
    q = xe.Quadrupole(name, length=l)
    assert q.name == name
    assert q.position_data.length == l
    md = Madx()
    q_conv = xe.Quadrupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv


@mark.parametrize('name,    l,   k1',
                 [( 'q1', 1.2, -1.3),
                  ( 'q2', 0.2,  1.1)])
def test_quadrupole_length_k1(name, l, k1):
    q = xe.Quadrupole(name, length=l, k1=k1)
    assert q.name == name
    assert q.length == l
    assert q.strength_data.k1 == k1
    md = Madx()
    q_conv = xe.Quadrupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv


@mark.parametrize('name,    l,  k1s',
                 [( 'q1', 1.2, -1.3),
                  ( 'q2', 0.2,  1.1)])
def test_quadrupole_length_k1s(name, l, k1s):
    q = xe.Quadrupole(name, length=l, k1s=k1s)
    assert q.name == name
    assert q.length == l
    assert q.strength_data.k1s == k1s
    md = Madx()
    q_conv = xe.Quadrupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv


@mark.parametrize('name,    l,   k1,  k1s',
                 [( 'q1', 1.2, -1.3,  1.3),
                  ( 'q2', 1.2,  1.3, -1.3),
                  ( 'q3', 1.2, -1.1, -1.3),
                  ( 'q4', 0.2,  1.1,  1.3)])
def test_quadrupole_length_k1_k1s(name, l, k1, k1s):
    q = xe.Quadrupole(name, length=l, k1=k1, k1s=k1s)
    assert q.name == name
    assert q.length == l
    assert q.strength_data.k1 == k1
    assert q.strength_data.k1s == k1s
    md = Madx()
    q_conv = xe.Quadrupole.from_cpymad(q.to_cpymad(md))
    assert q == q_conv

