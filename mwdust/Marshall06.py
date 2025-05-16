###############################################################################
#
#   Marshall06: extinction model from Marshall et al. 2006 2006A&A...453..635M
#
###############################################################################
import os, os.path
import sys
import gzip
import numpy
from scipy import interpolate
from astropy.io import ascii
from mwdust.util.extCurves import aebv
from mwdust.util.tools import cos_sphere_dist
from mwdust.util.download import dust_dir, downloader
from mwdust.DustMap3D import DustMap3D

try:
    from galpy.util import plot as bovy_plot
    _BOVY_PLOT_LOADED= True
except ImportError:
    _BOVY_PLOT_LOADED= False
from matplotlib import pyplot
_DEGTORAD= numpy.pi/180.
_marshalldir= os.path.join(dust_dir,'marshall06')
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
        self._marshalldata= ascii.read(os.path.join(_marshalldir,
                                                         'table1.dat'),
                                            readme=os.path.join(_marshalldir,
                                                                'ReadMe'),
                                            guess=False, format='cds',
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
            raise NotImplementedError("array input for l and b for Marshall06 dust map not implemented")
        lbIndx= self._lbIndx(l,b)
        if self._intps[lbIndx] != 0:
            out= self._intps[lbIndx](d)
        else:
            tlbData= self.lbData(l,b,addBC=True)
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
           2015-03-07 - Written - Bovy (IAS)
        """
        # Find all of the (l,b) of the pixels within radius of (lcen,bcen)
        lmin= round((lcen-radius-self._dl)/self._dl)*self._dl
        lmax= round((lcen+radius+self._dl)/self._dl)*self._dl
        bmin= round((bcen-radius-self._db)/self._db)*self._db
        bmax= round((bcen+radius+self._db)/self._db)*self._db
        ls= numpy.arange(lmin,lmax+self._dl,self._dl)
        bs= numpy.arange(bmin,bmax+self._db,self._db)
        ll,bb= numpy.meshgrid(ls,bs,indexing='ij')
        ll= ll.flatten()
        bb= bb.flatten()
        indx= cos_sphere_dist(numpy.sin((90.-bb)*_DEGTORAD),
                              numpy.cos((90.-bb)*_DEGTORAD),
                              numpy.sin(ll*_DEGTORAD),
                              numpy.cos(ll*_DEGTORAD),
                              numpy.sin((90.-bcen)*_DEGTORAD),
                              numpy.cos((90.-bcen)*_DEGTORAD),
                              numpy.sin(lcen*_DEGTORAD),
                              numpy.cos(lcen*_DEGTORAD)) \
                              >= numpy.cos(radius*_DEGTORAD)
        ll= ll[indx]
        bb= bb[indx]
        # Now get the extinctions for these pixels
        pixarea= self._dl*self._db*_DEGTORAD**2.+numpy.zeros(numpy.sum(indx))
        extinction= []
        for l,b in zip(ll,bb):
            extinction.append(self._evaluate(l,b,dist))
        extinction= numpy.array(extinction)
        return (pixarea,extinction)
               
    def dmax(self,l,b):
        """
        NAME:
           dmax
        PURPOSE:
           return the maximum distance for which there is Marshall et al. 
           (2006) data
        INPUT:
           l- Galactic longitude (deg)
           b- Galactic latitude (deg)
        OUTPUT:
           maximum distance in kpc
        HISTORY:
           2013-12-19 - Started - Bovy (IAS)
        """
        tlbData= self.lbData(l,b,addBC=False)
        return tlbData['dist'][-1]

    def lbData(self,l,b,addBC=False):
        """
        NAME:
           lbData
        PURPOSE:
           return the Marshall et al. (2006) data corresponding to a given
           line of sight
        INPUT:
           l- Galactic longitude (deg)
           b- Galactic latitude (deg)
           addBC= (False) if True, add boundary conditions (extinction is zero at zero distance; extinction is constant after last data point)
        OUTPUT:
        HISTORY:
           2013-12-13 - Written - Bovy (IAS)
        """
        #Find correct entry
        lbIndx= self._lbIndx(l,b)
        #Build output array
        out= numpy.recarray((self._marshalldata[lbIndx]['nb']+2*addBC,),
                            dtype=[('dist', 'f8'),
                                   ('e_dist', 'f8'),
                                   ('aks', 'f8'),
                                   ('e_aks','f8')])
        if addBC:
            #Add boundary conditions
            out[0]['dist']= 0.
            out[0]['e_dist']= 0.
            out[0]['aks']= 0.
            out[0]['e_aks']= 0.
            out[-1]['dist']= 30.
            out[-1]['e_dist']= 0.
            out[-1]['aks']= self._marshalldata[lbIndx]['ext%i' % (self._marshalldata[lbIndx]['nb'])]
            out[-1]['e_aks']=  self._marshalldata[lbIndx]['e_ext%i' % (self._marshalldata[lbIndx]['nb'])]
        for ii in range(self._marshalldata[lbIndx]['nb']):
            out[ii+addBC]['dist']= self._marshalldata[lbIndx]['r%i' % (ii+1)]
            out[ii+addBC]['e_dist']= self._marshalldata[lbIndx]['e_r%i' % (ii+1)]
            out[ii+addBC]['aks']= self._marshalldata[lbIndx]['ext%i' % (ii+1)]
            out[ii+addBC]['e_aks']= self._marshalldata[lbIndx]['e_ext%i' % (ii+1)]
        return out

    def plotData(self,l,b,*args,**kwargs):
        """
        NAME:
           plotData
        PURPOSE:
           plot the Marshall et al. (2006) extinction values 
           along a given line of sight as a function of 
           distance
        INPUT:
           l,b - Galactic longitude and latitude (degree)
           bovy_plot.plot args and kwargs
        OUTPUT:
           plot to output device
        HISTORY:
           2013-12-15 - Written - Bovy (IAS)
        """
        if not _BOVY_PLOT_LOADED:
            raise NotImplementedError("galpy.util.bovy_plot could not be loaded, so there is no plotting; might have to install galpy (http://github.com/jobovy/galpy) for plotting")
        #First get the data
        tdata= self.lbData(l,b)
        #Filter
        if self._filter is None:
            filterFac= 1./aebv('2MASS Ks',sf10=self._sf10)
        else:
            filterFac= 1./aebv('2MASS Ks',sf10=self._sf10)\
                *aebv(self._filter,sf10=self._sf10)
        #Plot
        out= bovy_plot.plot(tdata['dist'],tdata['aks']*filterFac,
                            *args,**kwargs)
        #uncertainties
        pyplot.errorbar(tdata['dist'],tdata['aks']*filterFac,
                        xerr=tdata['e_dist'],
                        yerr=tdata['e_aks']*filterFac,
                        ls='none',marker=None,color='k')
        return out

    def _lbIndx(self,l,b):
        """Return the index in the _marshalldata array corresponding to this (l,b)"""
        if l <= -100.125 or l >= 100.125 or b <= -10.125 or b >= 10.125:
            raise IndexError("Given (l,b) pair not within the region covered by the Marshall et al. (2006) dust map")
        lIndx= int(round((l+100.)/self._dl))
        bIndx= int(round((b+10.)/self._db))
        return lIndx*81+bIndx

    @classmethod
    def download(cls, test=False):
        marshall_folder_path = os.path.join(dust_dir, "marshall06")
        marshall_path = os.path.join(marshall_folder_path, "table1.dat.gz")
        marshall_readme_path = os.path.join(dust_dir, "marshall06", "ReadMe")
        if not os.path.exists(marshall_path[:-3]):
            if not os.path.exists(marshall_folder_path):
                os.mkdir(marshall_folder_path)
            _MARSHALL_URL= "https://cdsarc.cds.unistra.fr/ftp/J/A+A/453/635/table1.dat.gz"
            downloader(_MARSHALL_URL, marshall_path, cls.__name__, test=test)
            if not test:
                with open(marshall_path, "rb") as inf, open(os.path.join(marshall_folder_path, "table1.dat"), "w", encoding="utf8") as tof:
                    decom_str = gzip.decompress(inf.read()).decode("utf-8")
                    tof.write(decom_str)
                os.remove(marshall_path)
        if not os.path.exists(marshall_readme_path):
            _MARSHALL_README_URL= "https://cdsarc.cds.unistra.fr/ftp/J/A+A/453/635/ReadMe"
            downloader(_MARSHALL_README_URL, marshall_readme_path, f"{cls.__name__} (ReadMe)", test=test)
        return None
