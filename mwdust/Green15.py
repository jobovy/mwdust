###############################################################################
#
#   Green15: extinction model from Green et al. (2015)
#
###############################################################################
import os, os.path
import numpy
import h5py
from mwdust.DustMap3D import dust_dir, downloader
from mwdust.HierarchicalHealpixMap import HierarchicalHealpixMap
_DEGTORAD= numpy.pi/180.
_greendir= os.path.join(dust_dir, 'green15')
class Green15(HierarchicalHealpixMap):
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
        HierarchicalHealpixMap.__init__(self,filter=filter,sf10=sf10)
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

    def substitute_sample(self,samplenum):
        """
        NAME:
           substitute_sample
        PURPOSE:
           substitute a sample for the best fit to get the extinction from a sample with the same tools; need to have setup the instance with load_samples=True
        INPUT:
           samplenum - sample's index to load
        OUTPUT:
           (none; just resets the instance to use the sample rather than the best fit; one cannot go back to the best fit after this))
        HISTORY:
           2015-03-08 - Written - Bovy (IAS)
        """
        # Substitute the sample
        self._best_fit= self._samples[:,samplenum,:]
        # Reset the cache
        self._intps= numpy.zeros(len(self._pix_info['healpix_index']),
                                 dtype='object') #array to cache interpolated extinctions
        return None

    @classmethod
    def download(cls, test=False):
       # Download Green et al. PanSTARRS data (alt.: http://dx.doi.org/10.7910/DVN/40C44C)
       green15_path = os.path.join(dust_dir, "green15", "dust-map-3d.h5")
       if not os.path.exists(green15_path):
             if not os.path.exists(os.path.join(dust_dir, "green15")):
                os.mkdir(os.path.join(dust_dir, "green15"))
             _GREEN15_URL = "http://faun.rc.fas.harvard.edu/pan1/ggreen/argonaut/data/dust-map-3d.h5"
             downloader(_GREEN15_URL, green15_path, "GREEN15", test=test)
