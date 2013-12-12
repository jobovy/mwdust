###############################################################################
#
#   Marshall06: extinction model from Marshall et al. 2006 2006A&A...453..635M
#
###############################################################################
import os, os.path
import sys
import numpy
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
        #Sort the data on l and then b
        negIndx= self._marshalldata['GLON'] > 180.
        self._marshalldata['GLON'][negIndx]= self._marshalldata['GLON'][negIndx]-360.
        sortIndx= numpy.arange(len(self._marshalldata))
        keyArray= (self._marshalldata['GLON']+self._marshalldata['GLAT']/100.).data
        sortIndx= sorted(sortIndx,key=lambda x: keyArray[x])
        self._marshalldata= self._marshalldata[sortIndx]
        self._dl= 0.25
        self._db= 0.25
        return None

    def _evaluate(self,l,b,d,norescale=False):
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
           extinction
        HISTORY:
           2013-12-12 - Started - Bovy (IAS)
        """
        if isinstance(l,numpy.ndarray) or isinstance(b,numpy.ndarray):
            raise NotImplementedError("array input for l and b for Drimmel dust map not implemented")
        #Find correct entry
        lbIndx= self._lbIndx(l,b)
        return None

    def _lbIndx(self,l,b):
        """Return the index in the _marshalldata array corresponding to this (l,b)"""
        if l <= -100.125 or l >= 100.125 or b <= -10.125 or b >= 10.125:
            raise IndexError("Given (l,b) pair not within the region covered by the Marshall et al. (2006) dust map")
        lIndx= int(round((l+100.)/self._dl))
        bIndx= int(round((b+10.)/self._db))
        return lIndx*81+bIndx
