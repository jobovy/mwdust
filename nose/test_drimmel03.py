import numpy
from hypothesis import given, strategies, Settings
import mwdust

@given(strategies.floats(min_value=0.,max_value=360.,
                         allow_nan=False,allow_infinity=False),
       strategies.floats(min_value=-90.,max_value=90.,
                         allow_nan=False,allow_infinity=False),
       strategies.floats(min_value=0.,max_value=20.,
                         allow_nan=False,allow_infinity=False),
       settings=Settings(max_examples=50))
def test_avebv(ll,bb,dist):
    drim_av= mwdust.Drimmel03(filter='CTIO V')
    drim_ebv= mwdust.Drimmel03()
    assert numpy.fabs(drim_av(ll,bb,dist)/drim_ebv(ll,bb,dist)/0.86-3.1) < 0.02
    return None
