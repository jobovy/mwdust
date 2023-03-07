###############################################################################
#
#   Green17: extinction model from Green et al. (2017)
#
###############################################################################
import os, os.path
import numpy
import h5py
from mwdust.util.download import dust_dir, downloader
from mwdust.HierarchicalHealpixMap import HierarchicalHealpixMap
_DEGTORAD= numpy.pi/180.
_greendir= os.path.join(dust_dir, 'green17')
class Green17(HierarchicalHealpixMap):
    """extinction model from Green et al. (2018)"""
    def __init__(self,filter=None,sf10=True,load_samples=False,
                 interpk=1):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the Green et al. (2017) dust map
	   The reddening vector is not the one used in Green et al. (2015)
	   But instead: Schlafly et al. (2016)
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
           load_samples= (False) if True, also load the samples
           interpk= (1) interpolation order
        OUTPUT:
           object
        HISTORY:
           2019-10-09 - Adopted - Rybizki (MPIA)
        """
        HierarchicalHealpixMap.__init__(self,filter=filter,sf10=sf10)
        #Read the map
        with h5py.File(os.path.join(_greendir,'bayestar2017.h5'),'r') \
                as greendata:
            self._pix_info= greendata['/pixel_info'][:]
            if load_samples:
                self._samples= greendata['/samples'][:]
            self._best_fit= greendata['/best_fit'][:]
            self._GR= greendata['/GRDiagnostic'][:]
        # Utilities
        self._distmods= numpy.linspace(4,19,31)
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
           2019-10-09 - Adopted - Rybizki (MPIA)
        """
        # Substitute the sample
        self._best_fit= self._samples[:,samplenum,:]
        # Reset the cache
        self._intps= numpy.zeros(len(self._pix_info['healpix_index']),
                                 dtype='object') #array to cache interpolated extinctions
        return None

    @classmethod
    def download(cls, test=False):
        # Download Green et al. 2018 PanSTARRS data
        green17_path = os.path.join(dust_dir, "green17", "bayestar2017.h5")
        if not os.path.exists(green17_path):
            if not os.path.exists(os.path.join(dust_dir, "green17")):
                os.mkdir(os.path.join(dust_dir, "green17"))
            _GREEN17_URL = "https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/LCYHJG/S7MP4P"
            downloader(_GREEN17_URL, green17_path, cls.__name__, test=test)
        return None
