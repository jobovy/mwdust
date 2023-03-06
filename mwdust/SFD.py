###############################################################################
#
#   SFD: Schlegel, Finkbeiner, & Davis (1998) dust map (2D)
#
###############################################################################
import os
import numpy
from mwdust.util.download import downloader
from mwdust.util.read_SFD import read_SFD_EBV
from mwdust.util.extCurves import aebv
from mwdust.DustMap3D import DustMap3D, dust_dir, downloader


class SFD(DustMap3D):
    """Schlegel, Finkbeiner, & Davis (1998) dust map (2D)"""
    def __init__(self,filter=None,sf10=True,interp=True,noloop=False):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the SFD dust map
        INPUT:
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
           filter= filter to return the extinction in
           interp= (True) if True, interpolate using the nearest pixels
           noloop= (False) if True, don't loop through the glons
        OUTPUT:
           object
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        DustMap3D.__init__(self,filter=filter)
        self._sf10= sf10
        self._interp= interp
        self._noloop= noloop
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
           d- distance (kpc)
        OUTPUT:
           extinction
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        tebv= read_SFD_EBV(l,b,interp=self._interp,
                           noloop=self._noloop,verbose=False)
        if self._filter is None:
            return tebv*numpy.ones_like(d)
        else:
            return tebv*aebv(self._filter,sf10=self._sf10)*numpy.ones_like(d)

    @classmethod
    def download(cls, test=False):
          sfd_ngp_path = os.path.join(dust_dir, "maps", "SFD_dust_4096_ngp.fits")
          if not os.path.exists(sfd_ngp_path):
                if not os.path.exists(os.path.join(dust_dir, "maps")):
                   os.mkdir(os.path.join(dust_dir, "maps"))
                _SFD_URL_NGP= "https://svn.sdss.org/public/data/sdss/catalogs/dust/trunk/maps/SFD_dust_4096_ngp.fits"
                downloader(_SFD_URL_NGP, sfd_ngp_path, "SFD_NGP", test=test)
          sfd_sgp_path = os.path.join(dust_dir, "maps", "SFD_dust_4096_sgp.fits")
          if not os.path.exists(sfd_ngp_path):
                _SFD_URL_SGP= "https://svn.sdss.org/public/data/sdss/catalogs/dust/trunk/maps/SFD_dust_4096_sgp.fits"
                downloader(_SFD_URL_SGP, sfd_sgp_path, "SFD_SGP", test=test)
