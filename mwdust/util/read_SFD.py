import sys
import distutils.sysconfig as sysconfig
import ctypes
import ctypes.util
from numpy.ctypeslib import ndpointer
import os, os.path
import numpy
import platform
WIN32= platform.system() == 'Windows'
#Find and load the library
_lib = None
_libname = ctypes.util.find_library('sfd_c')
PY3= sys.version > '3'
if PY3: #pragma: no cover
    _ext_suffix= sysconfig.get_config_var('EXT_SUFFIX')
else:
    _ext_suffix= sysconfig.get_config_var('SO')
if _libname:
    _lib = ctypes.CDLL(_libname)
if _lib is None:
    for path in sys.path:
        try:
            _lib = ctypes.CDLL(os.path.join(path,'sfd_c%s' % _ext_suffix))
        except OSError:
            _lib = None
        else:
            break
if _lib is None and not WIN32:
    raise IOError('SFD/C module not found')

#MAP path names
dust_dir= os.getenv('DUST_DIR')
ebvFileN= os.path.join(dust_dir,'maps','SFD_dust_4096_ngp.fits')
ebvFileS= os.path.join(dust_dir,'maps','SFD_dust_4096_sgp.fits')

def read_SFD_EBV(glon,glat,interp=True,noloop=False,verbose=False):
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
    OUTPUT:
       array of E(B-V) from Schlegel, Finkbeiner, & Davis (1998)
    HISTORY:
       2013-11-23 - Written - Bovy (IAS)
    """
    #Parse input
    if isinstance(glon,(int,float,numpy.float32,numpy.float64)):
        glon= numpy.array([glon])
    if isinstance(glat,(int,float,numpy.float32,numpy.float64)):
        glat= numpy.array([glat])
        
    #Set up the C code
    ndarrayFlags= ('C_CONTIGUOUS','WRITEABLE')
    evalFunc= _lib.lambert_getval
    evalFunc.argtypes= [ctypes.c_char_p,
                        ctypes.c_char_p,
                        ctypes.c_long,
                        ndpointer(dtype=numpy.float32,flags=ndarrayFlags),
                        ndpointer(dtype=numpy.float32,flags=ndarrayFlags),
                        ctypes.c_int,
                        ctypes.c_int,
                        ctypes.c_int]
    evalFunc.restype= ctypes.POINTER(ctypes.c_float)

    #Array requirements, first store old order
    f_cont= [glon.flags['F_CONTIGUOUS'],
             glat.flags['F_CONTIGUOUS']]
    glon= numpy.require(glon,dtype=numpy.float64,requirements=['C','W'])
    glat= numpy.require(glat,dtype=numpy.float64,requirements=['C','W'])

    # Check that the filename isn't too long for the SFD code
    if len(ebvFileN.encode('ascii')) >= 120 \
            or len(ebvFileS.encode('ascii')) >= 120:
        raise RuntimeError('The path of the file that contains the SFD dust maps is too long; please shorten the path of DUST_DIR')

    res= evalFunc(ctypes.c_char_p(ebvFileN.encode('ascii')),
                     ctypes.c_char_p(ebvFileS.encode('ascii')),
                     ctypes.c_long(len(glon)),
                     glon.astype(numpy.float32,order='C',copy=False),
                     glat.astype(numpy.float32,order='C',copy=False),
                     ctypes.c_int(interp),
                     ctypes.c_int(noloop),
                     ctypes.c_int(verbose))

    result= numpy.fromiter(res,dtype=float,count=len(glon))

    #Reset input arrays
    if f_cont[0]: glon= numpy.asfortranarray(glon)
    if f_cont[1]: glat= numpy.asfortranarray(glat)

    return result
