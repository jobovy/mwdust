import sys
import sysconfig
import ctypes
import ctypes.util
from numpy.ctypeslib import ndpointer
import os, os.path
from pathlib import Path
import numpy
import platform
import tqdm
from mwdust.util.download import dust_dir

WIN32 = platform.system() == "Windows"
# Find and load the library
_lib = None
_libname = ctypes.util.find_library("sfd_c")
PY3 = sys.version > "3"
if PY3:  # pragma: no cover
    _ext_suffix = sysconfig.get_config_var("EXT_SUFFIX")
else:
    _ext_suffix = sysconfig.get_config_var("SO")
if _libname:
    _lib = ctypes.CDLL(_libname)
if _lib is None:
    # Add top-level mwdust repository directory for pip install (-e) .,
    # just becomes site-packages for regular install
    paths = sys.path
    paths.append(str(Path(__file__).parent.parent.parent.absolute()))
    for path in [Path(p) for p in paths]:
        if not path.is_dir():
            continue
        try:
            _lib = ctypes.CDLL(str(path / f"sfd_c{_ext_suffix}"))
        except OSError:
            _lib = None
        else:
            break
if _lib is None:
    raise IOError("SFD/C module not found")

# MAP path names
ebvFileN = os.path.join(dust_dir, "maps", "SFD_dust_4096_ngp.fits")
ebvFileS = os.path.join(dust_dir, "maps", "SFD_dust_4096_sgp.fits")


def read_SFD_EBV(glon, glat, interp=True, noloop=False, verbose=False, pbar=True):
    """
    NAME:
       read_SFD_EBV
    PURPOSE:
       read an E(B-V) value from the Schlegel, Finkbeiner, & Davis (1998) maps
    INPUT:
       glon - Galactic longitude (deg), can be an array
       glat - Galactic latitude (deg), can be an array
       interp= (True) if True, interpolate using the nearest pixels
       noloop= (False) if True, don't loop through the glons
       verbose= (False) if True, be verbose
       pbar= (True) if True, show progress bar
    OUTPUT:
       array of E(B-V) from Schlegel, Finkbeiner, & Davis (1998)
    HISTORY:
       2013-11-23 - Written - Bovy (IAS)
    """
    # Parse input
    if isinstance(glon, (int, float, numpy.float32, numpy.float64)):
        glon = numpy.array([glon])
    if isinstance(glat, (int, float, numpy.float32, numpy.float64)):
        glat = numpy.array([glat])

    nstar = len(glon)
    if nstar > 1 and pbar:
        pbar = tqdm.tqdm(total=nstar, leave=False)
        pbar_func_ctype = ctypes.CFUNCTYPE(None)
        pbar_c = pbar_func_ctype(pbar.update)
    else:  # pragma: no cover
        pbar_c = None

    # Set up the C code
    ndarrayFlags = ("C_CONTIGUOUS", "WRITEABLE")
    evalFunc = _lib.lambert_getval
    evalFunc.argtypes = [
        ctypes.c_char_p,
        ctypes.c_char_p,
        ctypes.c_long,
        ndpointer(dtype=numpy.float32, flags=ndarrayFlags),
        ndpointer(dtype=numpy.float32, flags=ndarrayFlags),
        ctypes.c_int,
        ctypes.c_int,
        ctypes.c_int,
        ndpointer(dtype=numpy.int32, flags=ndarrayFlags),
        ctypes.c_void_p,
    ]
    evalFunc.restype = ctypes.POINTER(ctypes.c_float)

    # Array requirements, first store old order
    f_cont = [glon.flags["F_CONTIGUOUS"], glat.flags["F_CONTIGUOUS"]]
    glon = numpy.require(glon, dtype=numpy.float64, requirements=["C", "W"])
    glat = numpy.require(glat, dtype=numpy.float64, requirements=["C", "W"])
    err = numpy.require(0, dtype=numpy.int32, requirements=["C", "W"])

    # Check that the filename isn't too long for the SFD code
    if len(ebvFileN.encode("ascii")) >= 120 or len(ebvFileS.encode("ascii")) >= 120:
        raise RuntimeError(
            f"The path of the file that contains the SFD dust maps is too long ({len(ebvFileN.encode('ascii'))}); please shorten the path of DUST_DIR"
        )

    res = evalFunc(
        ctypes.c_char_p(ebvFileN.encode("ascii")),
        ctypes.c_char_p(ebvFileS.encode("ascii")),
        ctypes.c_long(nstar),
        glon.astype(numpy.float32, order="C", copy=False),
        glat.astype(numpy.float32, order="C", copy=False),
        ctypes.c_int(interp),
        ctypes.c_int(noloop),
        ctypes.c_int(verbose),
        err,
        pbar_c,
    )
    if numpy.any(err == -10):
        raise KeyboardInterrupt("Interrupted by CTRL-C (SIGINT)")
    result = numpy.fromiter(res, dtype=float, count=nstar)

    # Reset input arrays
    if f_cont[0]:
        glon = numpy.asfortranarray(glon)
    if f_cont[1]:
        glat = numpy.asfortranarray(glat)

    return result
