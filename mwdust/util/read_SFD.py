import ctypes
import ctypes.util
from numpy.ctypeslib import ndpointer
import os, os.path
import numpy
#Find and load the library
_lib = None
_libname = ctypes.util.find_library('sfd_c')
if _libname:
    _lib = ctypes.CDLL(_libname)
if _lib is None:
    import sys
    for path in sys.path:
        try:
            _lib = ctypes.CDLL(os.path.join(path,'sfd_c.so'))
        except OSError:
            _lib = None
        else:
            break
if _lib is None:
    raise IOError('SFD/C module not found')

#MAP path names
dust_dir= os.getenv('DUST_DIR')
ebvFileN= os.path.join(dust_dir,'maps','SFD_dust_4096_ngp.fits')
ebvFileS= os.path.join(dust_dir,'maps','SFD_dust_4096_sgp.fits')

def read_SFD_EBV(glon,glat,interp=True,noloop=False,verbose=False):
    """I'll write documentation later"""
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

    res= evalFunc(ctypes.c_char_p(ebvFileN),
                     ctypes.c_char_p(ebvFileS),
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
