import pathlib
import numpy
from numpy.random import default_rng
rng= default_rng()


def test_distance_dependent():
    # Test that Green19 map is monotonic increase with distance
    # for a given line of sight.
    from mwdust import Green19
    green19= Green19()
    glons= rng.uniform(50.,220.,size=20)
    glats= rng.uniform(-90.,90.,size=20)
    dists= rng.uniform(0.01,1.,size=5)
    ebvs= numpy.array([[green19(glons[ii],glats[ii],dists[jj]) \
                            for ii in range(len(glons))]
                            for jj in range(len(dists))]).T     
    assert numpy.all(numpy.fabs(ebvs-ebvs[0])>=0), \
        'Green19 extinction is not monotonic increase with distance for at lease one given line of sight'
    return None


def test_against_known_values():
    # Test that the SFD extinction agrees with a table of known values
    # These were computed using mwdust on Linux using mwdust 0.12.0
    # before custom healpix functions are implemented (thus computed using healpy)
    from mwdust import Green19
    green19= Green19()
    known= numpy.loadtxt(pathlib.Path(__file__).parent / 'green19_benchmark.dat',delimiter=',')
    glons= known.T[0]
    glats= known.T[1]
    dists= known.T[2]
    ebvs= known.T[3]
    assert numpy.all(ebvs-[green19(glon,glat,dist)[0]
                            for glon,glat,dist in zip(glons,glats,dists)] < 10.**-8.), \
        'Green19 extinction does not agree with known values'
    return None
