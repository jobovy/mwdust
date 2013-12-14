###############################################################################
#
#   Marshall06: extinction model from Marshall et al. 2006 2006A&A...453..635M
#
###############################################################################
import os, os.path
import sys
import numpy
from scipy import interpolate
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
        self._intps= numpy.zeros(len(self._marshalldata),dtype='object') #array to cache interpolated extinctions
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
           extinction
        HISTORY:
           2013-12-12 - Started - Bovy (IAS)
        """
        if isinstance(l,numpy.ndarray) or isinstance(b,numpy.ndarray):
            raise NotImplementedError("array input for l and b for Drimmel dust map not implemented")
        lbIndx= self._lbIndx(l,b)
        if self._intps[lbIndx] != 0:
            out= self._intps[lbIndx](d)
        else:
            tlbData= self.lbData(l,b)
            interpData=\
                interpolate.InterpolatedUnivariateSpline(tlbData['dist'],
                                                         tlbData['aks'],
                                                         k=1)
            out= interpData(d)
            self._intps[lbIndx]= interpData
        if self._filter is None:
            return out/aebv('2MASS Ks',sf10=self._sf10)
        else:
            return out/aebv('2MASS Ks',sf10=self._sf10)\
                *aebv(self._filter,sf10=self._sf10)

    def lbData(self,l,b):
        """
        NAME:
           lbData
        PURPOSE:
           return the Marshall et al. (2006) data corresponding to a given
           line of sight
        INPUT:
           l- Galactic longitude (deg)
           b- Galactic latitude (deg)
        OUTPUT:
        HISTORY:
           2013-12-13 - Written - Bovy (IAS)
        """
        #Find correct entry
        lbIndx= self._lbIndx(l,b)
        #Build output array
        out= numpy.recarray((self._marshalldata[lbIndx]['nb']+1,),
                            dtype=[('dist', 'f8'),
                                   ('e_dist', 'f8'),
                                   ('aks', 'f8'),
                                   ('e_aks','f8')])
        out[0]['dist']= 0.
        out[0]['e_dist']= 0.
        out[0]['aks']= 0.
        out[0]['e_aks']= 0.
        for ii in range(1,self._marshalldata[lbIndx]['nb']+1):
            out[ii]['dist']= self._marshalldata[lbIndx]['r%i' % (ii)]
            out[ii]['e_dist']= self._marshalldata[lbIndx]['e_r%i' % (ii)]
            out[ii]['aks']= self._marshalldata[lbIndx]['ext%i' % (ii)]
            out[ii]['e_aks']= self._marshalldata[lbIndx]['e_ext%i' % (ii)]
        return out

    def _lbIndx(self,l,b):
        """Return the index in the _marshalldata array corresponding to this (l,b)"""
        if l <= -100.125 or l >= 100.125 or b <= -10.125 or b >= 10.125:
            raise IndexError("Given (l,b) pair not within the region covered by the Marshall et al. (2006) dust map")
        lIndx= int(round((l+100.)/self._dl))
        bIndx= int(round((b+10.)/self._db))
        return lIndx*81+bIndx
