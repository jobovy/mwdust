import sys
import distutils.sysconfig as sysconfig
import ctypes
import ctypes.util
from numpy.ctypeslib import ndpointer
import os
import numpy as np


# healpy number to represent bad numbers
UNSEEN = -1.6375e+30

# Find and load the library
_lib = None
_libname = ctypes.util.find_library("healpix_c")
_ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
if _libname:
    _lib = ctypes.CDLL(_libname)
if _lib is None:
    for path in sys.path:
        try:
            _lib = ctypes.CDLL(os.path.join(path, "healpix_c%s" % _ext_suffix))
        except OSError:
            _lib = None
        else:
            break
if _lib is None:
    raise IOError("healpix/C module not found")


# useful utilities: http://graphics.stanford.edu/~seander/bithacks.html#DetermineIfPowerOf2
def check_nside(nside, nest=False):
    """
    Utility function
    
    Check if healpix map with nside is valid in general
    """
    # nside can only be a power of 2 for nest, but generally less than 2**29
    nside_arr = np.array(nside).astype(np.int64)
    is_ok = True
    if nside == nside_arr and 0 < nside and nside <= 2**29:
        if nest:
            is_ok = (nside_arr & (nside_arr - 1)) == 0
    else:
        is_ok = False
    if not is_ok:
        raise ValueError(f"{nside} is not valid")


def check_npix(npix):
    """
    Utility function
    
    Check if total pixel number of a healpix map are valid in general
    """
    # check if npix is a valid value for healpix map size
    nside = np.sqrt(np.asarray(npix) / 12.0)
    if nside != np.floor(nside):
        raise ValueError(f"{npix} is not a valid value for healpix map size")


def check_ipix_nside(ipix, nside):
    """
    Utility function
    
    Check if pixel number(s) are valid in a healpix map with nside
    """
    # check if all ipix are valid for a healpix map size
    if not np.all(ipix <= nside2npix(nside)):
        raise ValueError(f"Not all ipix are valid for such healpix map size")


def npix2nside(npix):
    """
    Utility function

    Give the nside parameter for the given number of pixels.
    """
    check_npix(npix)
    return int(np.sqrt(npix / 12.0))


def lonlat2thetaphi(lon, lat):
    """
    NAME:
        lonlat2thetaphi
    PURPOSE:
        Angular coordinates convsrion: longitude and latitude (deg) to colatitude/longitude (rad)
    INPUT:
        lon, lat - longitude and latitude (deg)
    OUTPUT:
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    return np.pi / 2.0 - np.radians(lat), np.radians(lon)


def thetaphi2lonlat(theta, phi):
    """
    NAME:
        thetaphi2lonlat
    PURPOSE:
        Angular coordinates convsrion: colatitude/longitude (rad) to longitude and latitude (deg)
    INPUT:
        theta, phi - colatitude/longitude (rad)
    OUTPUT:
        lon, lat - longitude and latitude (deg)
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    return np.degrees(phi), 90.0 - np.degrees(theta)


def ang2pix(nside, theta, phi, nest=False, lonlat=False):
    """
    NAME:
        ang2pix
    PURPOSE:
        Angular coordinates to healpix map pixel number
    INPUT:
        nside - a integer of healpix map nside
        theta - colatitude
        phi - longitude
        nest - is using NEST?
        lonlat - input in longitude and latitude (deg)?
    OUTPUT:
        ipix - pixel numbers
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    check_nside(nside)
    theta, phi = np.atleast_1d(np.asarray(theta)), np.atleast_1d(np.asarray(phi))
    nstars = len(theta)
    if lonlat:
        theta, phi = lonlat2thetaphi(theta, phi)
    if nest is False:
        raise NotImplementedError("RING scheme is not avaliable for now")
        # ang2pix_c = _lib.ang2pix_ring
    else:
        ang2pix_c = _lib.ang2pix_nest
    ndarrayFlags = ("C_CONTIGUOUS", "WRITEABLE")
    
    ang2pix_c.argtypes = [
        ctypes.c_long,
        ndpointer(dtype=np.float64, flags=ndarrayFlags),
        ndpointer(dtype=np.float64, flags=ndarrayFlags),
        ctypes.c_long,
    ]
    ang2pix_c.restype = ctypes.POINTER(ctypes.c_longlong)

    # Array requirements, first store old order
    f_cont = [theta.flags["F_CONTIGUOUS"], phi.flags["F_CONTIGUOUS"]]
    theta = np.require(theta, dtype=np.float64, requirements=["C", "W"])
    phi = np.require(phi, dtype=np.float64, requirements=["C", "W"])
    res = ang2pix_c(
        ctypes.c_long(nside),
        theta.astype(np.float64, order="C", copy=False),
        phi.astype(np.float64, order="C", copy=False),
        ctypes.c_long(nstars),
    )
    result = np.fromiter(res, dtype=np.int32, count=nstars)

    # Reset input arrays
    if f_cont[0]:
        theta = np.asfortranarray(theta)
    if f_cont[1]:
        phi = np.asfortranarray(phi)

    return result


def ang2vec(theta, phi, lonlat=False):
    """
    NAME:
        ang2vec
    PURPOSE:
        Angular coordinates to unit 3-vector direction
    INPUT:
        theta - colatitude
        phi - longitude 
        lonlat - input in longitude and latitude (deg)?
    OUTPUT:
        x, y, z - unit 3-vector direction
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    theta, phi = np.atleast_1d(np.asarray(theta)), np.atleast_1d(np.asarray(phi))
    nstars = len(theta)
    if lonlat:
        theta, phi = lonlat2thetaphi(theta, phi)

    ang2vec_c = _lib.ang2vec
    ndarrayFlags = ("C_CONTIGUOUS", "WRITEABLE")
    
    ang2vec_c.argtypes = [
        ndpointer(dtype=np.float64, flags=ndarrayFlags),
        ndpointer(dtype=np.float64, flags=ndarrayFlags),
        ctypes.c_long,
    ]
    ang2vec_c.restype = ctypes.POINTER(ctypes.c_double)

    # Array requirements, first store old order
    f_cont = [theta.flags["F_CONTIGUOUS"], phi.flags["F_CONTIGUOUS"]]
    theta = np.require(theta, dtype=np.float64, requirements=["C", "W"])
    phi = np.require(phi, dtype=np.float64, requirements=["C", "W"])
    res = ang2vec_c(
        theta.astype(np.float64, order="C", copy=False),
        phi.astype(np.float64, order="C", copy=False),
        ctypes.c_long(nstars),
    )
    result = np.fromiter(res, dtype=np.float64, count=nstars*3)
    result = result.reshape(nstars, 3)

    # Reset input arrays
    if f_cont[0]:
        theta = np.asfortranarray(theta)
    if f_cont[1]:
        phi = np.asfortranarray(phi)

    return result

def pix2vec(nside, ipix, nest=False):
    """
    NAME:
        pix2vec
    PURPOSE:
        Pixel number to unit 3-vector direction
    INPUT:
        nside - a integer of healpix map nside
        ipix - a (list) of integer of pixel number
        nest - is using NEST?
    OUTPUT:
        x, y, z - unit 3-vector direction
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    ipix = np.asarray(ipix)
    check_nside(nside, nest=nest)
    check_ipix_nside(ipix, nside)
    ipix = np.atleast_1d(ipix)
    npix = len(ipix)
    if nest:
        pix2vec_c = _lib.pix2vec_nest
    else:
        raise NotImplementedError("RING scheme is not avaliable for now")
        # _lib.pix2ang_ring
    ndarrayFlags = ("C_CONTIGUOUS", "WRITEABLE")
    # (int nside, int npix, long long int *ipix)
    pix2vec_c.argtypes = [
        ctypes.c_long,
        ctypes.c_long,
        ndpointer(dtype=np.int64, flags=ndarrayFlags),
    ]
    pix2vec_c.restype = ctypes.POINTER(ctypes.c_double)

    # Array requirements, first store old order
    f_cont = [ipix.flags["F_CONTIGUOUS"]]
    ipix = np.require(ipix, dtype=np.int64, requirements=["C", "W"])
    res = pix2vec_c(
        nside,
        npix,
        ipix.astype(np.int64, order="C", copy=False),
    )
    result = np.fromiter(res, dtype=np.float64, count=npix*3)
    result = result.reshape(npix, 3)

    # Reset input arrays
    if f_cont[0]:
        ipix = np.asfortranarray(ipix)

    x, y, z = result[:, 0], result[:, 1], result[:, 2]
    return x, y, z


def pix2ang(nside, ipix, nest=False, lonlat=False):
    """
    NAME:
        pix2ang
    PURPOSE:
        Pixel number to angular coordinates
    INPUT:
        nside - a integer of healpix map nside
        ipix - a (list) of integer of pixel number
        nest - is using NEST?
        lonlat - output in longitude and latitude (deg)?
    OUTPUT:
        theta, phi - angular coordinates
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    ipix = np.asarray(ipix)
    check_nside(nside, nest=nest)
    check_ipix_nside(ipix, nside)
    ipix = np.atleast_1d(ipix)
    npix = len(ipix)
    if nest:
        pix2ang_c = _lib.pix2ang_nest
    else:
        raise NotImplementedError("RING scheme is not avaliable for now")
        # _lib.pix2ang_ring
    ndarrayFlags = ("C_CONTIGUOUS", "WRITEABLE")
    # (int nside, int npix, long long int *ipix)
    pix2ang_c.argtypes = [
        ctypes.c_long,
        ctypes.c_long,
        ndpointer(dtype=np.int64, flags=ndarrayFlags),
    ]
    pix2ang_c.restype = ctypes.POINTER(ctypes.c_double)

    # Array requirements, first store old order
    f_cont = [ipix.flags["F_CONTIGUOUS"]]
    ipix = np.require(ipix, dtype=np.int64, requirements=["C", "W"])
    res = pix2ang_c(
        nside,
        npix,
        ipix.astype(np.int64, order="C", copy=False),
    )
    result = np.fromiter(res, dtype=np.float64, count=npix*2)
    result = result.reshape(npix, 2)

    # Reset input arrays
    if f_cont[0]:
        ipix = np.asfortranarray(ipix)

    theta, phi = result[:, 0], result[:, 1]

    if lonlat:
        return thetaphi2lonlat(theta, phi)
    else:
        return theta, phi


def nside2pixarea(nside):
    """
    NAME:
        nside2pixarea
    PURPOSE:
        Get area of a pixel for a healpix map with nside
    INPUT:
        nside - a integer of healpix map nside
    OUTPUT:
        pixarea - a float of healpix map pixel area
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    return np.pi / (3 * nside ** 2)


def nside2npix(nside):
    """
    NAME:
        nside2npix
    PURPOSE:
        Get how many pixel for a healpix map with nside
    INPUT:
        nside - a integer of healpix map nside
    OUTPUT:
        npix - a integer of number of healpix map pixel
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    return 12 * nside * nside


def ud_grade(map_in, nside_plot, pess=False, order_in="RING", order_out=None, power=None, dtype=None):
    """
    NAME:
        dust_vals_disk
    PURPOSE:
        Upgrade or degrade healpix map
    INPUT:
        map_in - healpix map to be upgraded or degraded
        nside_plot - nside of the output map wanted
    OUTPUT:
        map_out - arrays of upgraded or degraded map(s)
    HISTORY:
        2023-03-01 - Written - Henry Leung (Toronto)
    """
    # check if arguements are implemented
    if order_in != "NEST" or (order_out is not None and order_out != "NEST"):
        raise NotImplementedError("order_in and order_out for RING scheme is not implemented for now")
    if power is not None:
        raise NotImplementedError("power is not implemented for now")
    if pess is not False:
        raise NotImplementedError("pess=True is not implemented for now")
    if dtype is not False:
        raise NotImplementedError("dtype is implemented for now, output map always has the same dtype as input map")
    check_nside(nside_plot, nest=order_in != "RING")
    map_in = np.asarray(map_in)

    num_of_map = len(np.atleast_2d(map_in))
    if num_of_map != 1:
        raise ValueError("This function only support one map at each time")
    
    nside_in = npix2nside(len(map_in))
    npix_in = nside2npix(nside_in)
    npix_out = nside2npix(nside_in)

    if nside_plot > nside_in: # upgrade
        rat2 = npix_out // npix_in
        fact = np.ones(rat2, dtype=map_in.dtype)
        map_out = np.outer(map_in, fact).reshape(npix_out)
    elif nside_plot < nside_in: # degrade
        rat2 = npix_in // npix_out
        mr = map_in.reshape(npix_out, rat2)
        goods = ~(np.isclose(mr, UNSEEN) | (~np.isfinite(mr)) | (~np.isnan(mr)))
        map_out = np.sum(mr * goods, axis=1)
        nhit = goods.sum(axis=1)
        map_out[nhit != 0] = map_out[nhit != 0] / nhit[nhit != 0]
        try:
            map_out[nhit == 0] = UNSEEN
        except OverflowError:
            pass
    else:
        map_out = map_in
        
    return map_out