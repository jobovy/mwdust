###############################################################################
#
#   DECaPS25: extinction model from Zucker et al. (2025)
#
###############################################################################
import os, os.path
import numpy
import h5py
from mwdust.util.download import dust_dir, downloader
from mwdust.HierarchicalHealpixMap import HierarchicalHealpixMap

_DEGTORAD = numpy.pi/180.
_decapsdir = os.path.join(dust_dir, 'zucer25')

class Zucker25(HierarchicalHealpixMap):
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
        HierarchicalHealpixMap.__init__(self, filter=filter, sf10=sf10, samples=load_samples)
        if not os.path.isdir(_decapsdir):
            os.mkdir(_decapsdir)
        fname = 'decaps_mean_and_samples.h5' if load_samples else 'decaps_mean.h5'
        fpath = os.path.join(_decapsdir, fname)
        if not os.path.exists(fpath):
            self.download(samples=load_samples)
        self._f = h5py.File(fpath, 'r')
        self._best_fit = self._f['/mean'][:, 0, :]
        p = self._f['/pixel_info']
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
        if load_samples:
            if 'samples' not in self._f:
                raise RuntimeError("Requested load_samples=True, but 'samples' dataset not found.")
            self._samples_dset = self._f['/samples']
        else:
            self._samples_dset = None
        self._minnside = numpy.amin(self._pix_info['nside'])
        self._maxnside = numpy.amax(self._pix_info['nside'])
        nlevels = int(numpy.log2(self._maxnside // self._minnside)) + 1
        self._nsides = [self._maxnside // 2**ii for ii in range(nlevels)]
        self._indexArray = numpy.arange(len(self._pix_info['healpix_index']))
        self._intps = numpy.zeros(len(self._pix_info['healpix_index']), dtype='object')
        self._interpk = interpk
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
        if self._samples_dset is None:
            raise RuntimeError('No samples present in DECaPS file')
        self._best_fit = self._samples_dset[:, samplenum, :]
        self._intps = numpy.zeros(len(self._pix_info['healpix_index']), dtype='object')
        return None

    @classmethod
    def download(cls, samples=False, test=False):
        subdir = os.path.join(dust_dir, "decaps25")
        if not os.path.exists(subdir):
            os.mkdir(subdir)
        if samples:
            target = os.path.join(subdir, "decaps_mean_and_samples.h5")
            url = "https://dataverse.harvard.edu/api/access/datafile/11840498"
        else:
            target = os.path.join(subdir, "decaps_mean.h5")
            url = "https://dataverse.harvard.edu/api/access/datafile/11838924"
        if not os.path.exists(target):
            downloader(url, target, cls.__name__, test=test)
        return None

    def __del__(self):
        try:
            if hasattr(self, "_f") and self._f:
                self._f.close()
        except Exception:
            pass
