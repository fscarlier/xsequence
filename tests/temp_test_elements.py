import pytest
import elements as el
import numpy as np


@pytest.mark.parametrize("length, angle", np.random.random((20,2)) )
def test_rbend_to_sbend(length, angle):
    rb = el.Rbend('rbend', length=length, angle=angle)
    rb2 = rb.convert_to_sbend().convert_to_rbend()
    assert rb == rb2

@pytest.mark.parametrize("length, angle", np.random.random((20,2)) )
def test_sbend_to_rbend(length, angle):
    sb = el.Sbend('rbend', length=length, angle=angle)
    sb2 = sb.convert_to_rbend().convert_to_sbend()
    assert sb == sb2




