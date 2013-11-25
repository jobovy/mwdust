###############################################################################
#
#   Marshall06: extinction model from Marshall et al. 2006 2006A&A...453..635M
#
###############################################################################
import os, os.path
import sys
import asciitable
from mwdust.util.extCurves import aebv
from DustMap3D import DustMap3D
_marshalldir= os.path.join(os.getenv('DUST_DIR'),'marshall06')
_ERASESTR= "                                                                                "
class Marshall06(DustMap3D):
    """extinction model from Marshall et al. 2006 2006A&A...453..635M"""
    def __init__(self,filter=None,sf10=True):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the Marshall06 dust map
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
        OUTPUT:
           object
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        DustMap3D.__init__(self,filter=filter)
        self._sf10= sf10
        #Read the maps
        sys.stdout.write('\r'+"Reading Marshall et al. (2006) data file ...\r")
        sys.stdout.flush()
        self._marshalldata= asciitable.read(os.path.join(_marshalldir,
                                                         'table1.dat'),
                                            readme=os.path.join(_marshalldir,
                                                                'ReadMe'),
                                            Reader=asciitable.cds.Cds,
                                            guess=False,
                                            fill_values=[('', '-999')])
        sys.stdout.write('\r'+_ERASESTR+'\r')
        sys.stdout.flush()
        return None

