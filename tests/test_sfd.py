import pathlib
import numpy
from numpy.random import default_rng
rng= default_rng()

def test_distance_independent():
    # Test that the SFD extinction is indepdendent of distance 
    # for a given line of sight.
    from mwdust import SFD
    sfd= SFD()
    glons= rng.uniform(0.,360.,size=20)
    glats= rng.uniform(-90.,90.,size=20)
    dists= rng.uniform(0.1,10.,size=5)
    ebvs= numpy.array([[sfd(glons[ii],glats[ii],dists[jj]) \
                            for ii in range(len(glons))]
                            for jj in range(len(dists))]).T     
    assert numpy.all(numpy.fabs(ebvs-ebvs[0]) < 10.**-10.), \
        'SFD extinction is not independent of distance for a given line of sight'
    return None

def test_against_known_values():
    # Test that the SFD extinction agrees with a table of known values
    # These were computed using mwdust on an M1 mac, so this test is really
    # of consistency between other OSs and architectures
    from mwdust import SFD
    sfd= SFD(interp=False)
    known= numpy.loadtxt(pathlib.Path(__file__).parent / 'sfd_benchmark.dat',delimiter=',')
    glons= known.T[0]
    glats= known.T[1]
    ebvs= known.T[2]
    assert numpy.all(ebvs-[sfd(glon,glat,1.)[0]
                            for glon,glat in zip(glons,glats)] < 10.**-8.), \
        'SFD extinction does not agree with known values'
    return None
