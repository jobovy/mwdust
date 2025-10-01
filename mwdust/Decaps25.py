from __future__ import division, print_function
import os, os.path
import numpy
import h5py
from mwdust.util.download import dust_dir, downloader
from mwdust.HierarchicalHealpixMap import HierarchicalHealpixMap

_DEGTORAD = numpy.pi/180.
_decapsdir = os.path.join(dust_dir, 'decaps25')

class Decaps25(HierarchicalHealpixMap):
    """DECaPS 3D dust-reddening map (Zucker et al. 2025)"""
    def __init__(self, filter=None, sf10=True, load_samples=False, interpk=1):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the DECaPS (2025) dust map
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
           load_samples= (False) if True, also load the samples
           interpk= (1) interpolation order
        OUTPUT:
           object
        HISTORY:
           2025-10-01 - Adopted
        """
        HierarchicalHealpixMap.__init__(self, filter=filter, sf10=sf10)
        with h5py.File(os.path.join(_decapsdir, 'decaps_mean.h5'), 'r') as f:
            mean = f['/mean'][:]
            self._best_fit = mean[:, 0, :].astype(numpy.float32)
            p = f['/pixel_info']
            hpx = p['healpix_index'][:]
            nside_attr = int(p.attrs['nside'])
            pix_dtype = numpy.dtype([('healpix_index', hpx.dtype), ('nside', numpy.int64)])
            self._pix_info = numpy.empty(hpx.shape[0], dtype=pix_dtype)
            self._pix_info['healpix_index'] = hpx
            self._pix_info['nside'] = nside_attr
            dm = numpy.array(p.attrs['DM_bin_edges'], dtype=numpy.float64)
            if dm.shape[0] != self._best_fit.shape[1]:
                raise RuntimeError("DM_bin_edges length does not match radial dimension")
            self._distmods = dm
        self._minnside = numpy.amin(self._pix_info['nside'])
        self._maxnside = numpy.amax(self._pix_info['nside'])
        nlevels = int(numpy.log2(self._maxnside // self._minnside)) + 1
        self._nsides = [self._maxnside // 2**ii for ii in range(nlevels)]
        self._indexArray = numpy.arange(len(self._pix_info['healpix_index']))
        self._intps = numpy.zeros(len(self._pix_info['healpix_index']), dtype='object')
        self._interpk = interpk
        if load_samples:
            self._samples = None
        return None

    def substitute_sample(self, samplenum):
        """
        NAME:
           substitute_sample
        PURPOSE:
           substitute a sample for the best fit to get the extinction from a sample with the same tools; need to have setup the instance with load_samples=True
        INPUT:
           samplenum - sample's index to load
        OUTPUT:
           (none; just resets the instance to use the sample rather than the best fit)
        HISTORY:
           2025-10-01 - Adopted
        """
        if not hasattr(self, '_samples') or self._samples is None:
            raise RuntimeError('No samples present in DECaPS file')
        self._best_fit = self._samples[:, samplenum, :]
        self._intps = numpy.zeros(len(self._pix_info['healpix_index']), dtype='object')
        return None

    @classmethod
    def download(cls, test=False):
        decaps25_path = os.path.join(dust_dir, "decaps25", "decaps_mean.h5")
        if not os.path.exists(decaps25_path):
            if not os.path.exists(os.path.join(dust_dir, "decaps25")):
                os.mkdir(os.path.join(dust_dir, "decaps25"))
            _DECAPS25_URL = "https://dataverse.harvard.edu/api/access/datafile/11838924"
            downloader(_DECAPS25_URL, decaps25_path, cls.__name__, test=test)
        return None
