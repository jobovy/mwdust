###############################################################################
#
#   Green15: extinction model from Green et al. (2015)
#
###############################################################################
import os, os.path
import numpy
import h5py
from scipy import interpolate
import healpy
from mwdust.util.extCurves import aebv
from DustMap3D import DustMap3D
_DEGTORAD= numpy.pi/180.
_greendir= os.path.join(os.getenv('DUST_DIR'),'green15')
class Green15(DustMap3D):
    """extinction model from Green et al. (2015)"""
    def __init__(self,filter=None,sf10=True,load_samples=False,
                 interpk=1):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the Green et al. (2015) dust map
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
           load_samples= (False) if True, also load the samples
           interpk= (1) interpolation order
        OUTPUT:
           object
        HISTORY:
           2015-03-02 - Started - Bovy (IAS)
        """
        DustMap3D.__init__(self,filter=filter)
        self._sf10= sf10
        #Read the map
        with h5py.File(os.path.join(_greendir,'dust-map-3d.h5'),'r') \
                as greendata:
            self._pix_info= greendata['/pixel_info'][:]
            if load_samples:
                self._samples= greendata['/samples'][:]
            self._best_fit= greendata['/best_fit'][:]
            self._GR= greendata['/GRDiagnostic'][:]
        # Utilities
        self._distmods= numpy.linspace(4.,19.,31)
        self._minnside= numpy.amin(self._pix_info['nside'])
        self._maxnside= numpy.amax(self._pix_info['nside'])
        nlevels= int(numpy.log2(self._maxnside//self._minnside))+1
        self._nsides= [self._maxnside//2**ii for ii in range(nlevels)]
        self._indexArray= numpy.arange(len(self._pix_info['healpix_index']))
        # For the interpolation
        self._intps= numpy.zeros(len(self._pix_info['healpix_index']),
                                 dtype='object') #array to cache interpolated extinctions
        self._interpk= interpk
        return None

    def _evaluate(self,l,b,d):
        """
        NAME:
           _evaluate
        PURPOSE:
           evaluate the dust-map
        INPUT:
           l- Galactic longitude (deg)
           b- Galactic latitude (deg)
           d- distance (kpc) can be array
        OUTPUT:
           extinction E(B-V)
        HISTORY:
           2015-03-02 - Started - Bovy (IAS)
        """
        distmod= 5.*numpy.log10(d)+10.
        if isinstance(l,numpy.ndarray) or isinstance(b,numpy.ndarray):
            raise NotImplementedError("array input for l and b for Green et al. dust map not implemented")
        lbIndx= self._lbIndx(l,b)
        if self._intps[lbIndx] != 0:
            out= self._intps[lbIndx][0](distmod)
        else:
            interpData=\
                interpolate.InterpolatedUnivariateSpline(self._distmods,
                                                         self._best_fit[lbIndx],
                                                         k=self._interpk)
            out= interpData(distmod)
            self._intps[lbIndx]= interpData
        if self._filter is None:
            return out
        else:
            return out*aebv(self._filter,sf10=self._sf10)

    def _lbIndx(self,l,b):
        """Return the index in the _greendata array corresponding to this (l,b)"""
        for nside in self._nsides:
            # Search for the pixel in this Nside level
            tpix= healpy.pixelfunc.ang2pix(nside,(90.-b)*_DEGTORAD,
                                           l*_DEGTORAD,nest=True)
            indx= (self._pix_info['healpix_index'] == tpix)\
                *(self._pix_info['nside'] == nside)
            if numpy.sum(indx) == 1:
                return self._indexArray[indx]
            elif numpy.sum(indx) > 1:
                raise IndexError("Given (l,b) pair has multiple matches!")
        raise IndexError("Given (l,b) pair not within the region covered by the Green et al. (2015) dust map")

