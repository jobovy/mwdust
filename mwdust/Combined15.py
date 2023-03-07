###############################################################################
#
#   Combined15: extinction model obtained from a combination of Marshall et al.
#               (2006), Green et al. (2015), and Drimmel et al. (2003)
#
###############################################################################
import os, os.path
import numpy
import h5py
from mwdust.util.download import downloader, dust_dir
from mwdust.HierarchicalHealpixMap import HierarchicalHealpixMap
_DEGTORAD= numpy.pi/180.
_combineddir= os.path.join(dust_dir, 'combined15')
class Combined15(HierarchicalHealpixMap):
    """extinction model obtained from a combination of Marshall et al.
    (2006), Green et al. (2015), and Drimmel et al. (2003)"""
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
        """
        HierarchicalHealpixMap.__init__(self,filter=filter,sf10=sf10)
        #Read the map
        with h5py.File(os.path.join(_combineddir,'dust-map-3d.h5'),'r') \
                as combineddata:
            self._pix_info= combineddata['/pixel_info'][:]
            self._best_fit= combineddata['/best_fit'][:]
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
    
    @classmethod
    def download(cls, test=False):
        # Download the combined map of Bovy et al. (2015): Marshall+Green+Drimmel for full sky coverage
        combined15_path = os.path.join(dust_dir, "combined15", "dust-map-3d.h5")
        if not os.path.exists(combined15_path):
                if not os.path.exists(os.path.join(dust_dir, "combined15")):
                    os.mkdir(os.path.join(dust_dir, "combined15"))
                _COMBINED15_URL = "https://zenodo.org/record/31262/files/dust-map-3d.h5"
                downloader(_COMBINED15_URL, combined15_path, cls.__name__, test=test)
        return None