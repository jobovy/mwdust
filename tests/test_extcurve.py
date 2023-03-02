import numpy
from numpy.random import default_rng
rng= default_rng()

def test_avebv():
    # Simple test of the extinction curve, using SFD as an example
    # Test that A_V/E(B-V) = 3.1 for the CTIO V filter
    from mwdust import SFD
    sfd_av= SFD(filter='CTIO V')
    sfd_ebv= SFD()
    glons= rng.uniform(0.,360.,size=20)
    glats= rng.uniform(-90.,90.,size=20)
    dists= rng.uniform(0.1,10.,size=5)
    for ll,bb,dist in zip(glons,glats,dists):
        assert numpy.fabs(sfd_av(ll,bb,dist)/sfd_ebv(ll,bb,dist)/0.86-3.1) < 0.02, \
            'SFD extinction curve for CTIO V does not agree with known values for A_V/E(B-V) = 3.1'
    return None
