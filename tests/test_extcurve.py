from datetime import timedelta
from hypothesis import given, strategies, settings
import numpy

@given(strategies.floats(min_value=0.,max_value=360.,
                         allow_nan=False,allow_infinity=False),
       strategies.floats(min_value=-90.,max_value=90.,
                         allow_nan=False,allow_infinity=False),
       strategies.floats(min_value=0.,max_value=20.,
                         allow_nan=False,allow_infinity=False))
@settings(max_examples=20,
          deadline=timedelta(milliseconds=100000))
def test_avebv(ll,bb,dist):
    # Simple test of the extinction curve, using Drimmel03 as an example
    # Test that A_V/E(B-V) = 3.1 for the CTIO V filter
    from mwdust import SFD
    sfd_av= SFD(filter='CTIO V')
    sfd_ebv= SFD()
    assert numpy.fabs(sfd_av(ll,bb,dist)/sfd_ebv(ll,bb,dist)/0.86-3.1) < 0.02
    return None
