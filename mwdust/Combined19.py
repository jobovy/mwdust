###############################################################################
#
#   Combined19: extinction model obtained from a combination of Marshall et al.
#               (2006), Green et al. (2019), and Drimmel et al. (2003)
#
###############################################################################
import os, os.path
import numpy
import h5py
from mwdust.HierarchicalHealpixMap import HierarchicalHealpixMap
_DEGTORAD= numpy.pi/180.
_combineddir= os.path.join(os.getenv('DUST_DIR'),'combined19')
class Combined19(HierarchicalHealpixMap):
    """extinction model obtained from a combination of Marshall et al.
    (2006), Green et al. (2019), and Drimmel et al. (2003)"""
    def __init__(self,filter=None,sf10=True,load_samples=False,
                 interpk=1):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the combined dust map
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
           interpk= (1) interpolation order
        OUTPUT:
           object
        HISTORY:
           2015-07-28 - Started - Bovy (UofT)
           2019-09-12 - Updated - Rybizki (MPIA)	   
        """
        HierarchicalHealpixMap.__init__(self,filter=filter,sf10=sf10)
        #Read the map
        with h5py.File(os.path.join(_combineddir,'combine19.h5'),'r') \
                as combineddata:
            self._pix_info= combineddata['/pixel_info'][:]
            self._best_fit= combineddata['/best_fit'][:]
        # Utilities
        self._distmods= numpy.linspace(4,18.875,120)
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
