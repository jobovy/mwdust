###############################################################################
#
#   Drimmel03: extinction model from Drimmel et al. 2003 2003A&A...409..205D
#
###############################################################################
import numpy
from mwdust.util.extCurves import aebv
from mwdust.util import read_Drimmel
from DustMap3D import DustMap3D
_DEGTORAD= numpy.pi/180.
class Drimmel03(DustMap3D):
    """extinction model from Drimmel et al. 2003 2003A&A...409..205D"""
    def __init__(self,filter=None,sf10=True):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the Drimmel03 dust map
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
        OUTPUT:
           object
        HISTORY:
           2013-12-10 - Started - Bovy (IAS)
        """
        DustMap3D.__init__(self,filter=filter)
        self._sf10= sf10
        #Read the maps
        drimmelMaps= read_Drimmel.readDrimmelAll()
        self._drimmelMaps= drimmelMaps
        #Sines and cosines of sky positions of COBE pixels
        self._rf_sintheta= numpy.sin(numpy.pi/2.-self._drimmelMaps['rf_glat']*_DEGTORAD)
        self._rf_costheta= numpy.cos(numpy.pi/2.-self._drimmelMaps['rf_glat']*_DEGTORAD)
        self._rf_sinphi= numpy.sin(self._drimmelMaps['rf_glon']*_DEGTORAD)
        self._rf_cosphi= numpy.cos(self._drimmelMaps['rf_glon']*_DEGTORAD)
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
           2013-12-10 - Started - Bovy (IAS)
        """
        #Find nearest pixel in COBE map for the re-scaling
        rfIndx= numpy.argmax(cos_sphere_dist(self._rf_sintheta,
                                             self._rf_costheta,
                                             self._rf_sinphi,
                                             self._rf_cosphi,
                                             numpy.sin(numpy.pi/2.-b*_DEGTORAD),
                                             numpy.cos(numpy.pi/2.-b*_DEGTORAD),
                                             numpy.sin(l*_DEGTORAD),
                                             numpy.cos(l*_DEGTORAD)))
        return rfIndx

def cos_sphere_dist(sintheta,costheta,
                    sinphi,cosphi,
                    sintheta_o,costheta_o,
                    sinphi_o,cosphi_o):
    """
    NAME:
       cos_sphere_dist
    PURPOSE:
       computes the cosine of the spherical distance between two
       points on the sphere
    INPUT:
       theta  - polar angle [0,pi]
       phi    - azimuth [0,2pi]
       theta  - polar angle of center of the disk
       phi_0  - azimuth of the center of the disk
    OUTPUT:
       spherical distance
    HISTORY:
       2010-04-29 -Written - Bovy (NYU)
    """
    return (sintheta*sintheta_o
            *(cosphi_o*cosphi+
              sinphi_o*sinphi)+
            costheta_o*costheta)
