###############################################################################
#
#   Zero: model with zero extinction
#
###############################################################################
import numpy
from DustMap3D import DustMap3D
_DEGTORAD= numpy.pi/180.
class Zero(DustMap3D):
    """model with zero extinction"""
    def __init__(self,filter=None,sf10=True):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the zero extinction model
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
        OUTPUT:
           Instance
        HISTORY:
           2015-03-07 - Written - Bovy (IAS)
        """
        DustMap3D.__init__(self,filter=filter)
        self._sf10= sf10
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
           2015-03-07 - Written - Bovy (IAS)
        """
        return numpy.zeros_like(d)

    def dust_vals_disk(self,lcen,bcen,dist,radius):
        """
        NAME:
           dust_vals_disk
        PURPOSE:
           return the distribution of extinction within a small disk as samples
        INPUT:
           lcen, bcen - Galactic longitude and latitude of the center of the disk (deg)
           dist - distance in kpc
           radius - radius of the disk (deg)
        OUTPUT:
           (pixarea,extinction) - arrays of pixel-area in sq rad and extinction value
        HISTORY:
           2015-03-06 - Written - Bovy (IAS)
        """
        pixarea= (1.-numpy.cos(radius*_DEGTORAD))*2.*numpy.pi
        return (numpy.array([pixarea]),numpy.zeros((1,len(dist))))

