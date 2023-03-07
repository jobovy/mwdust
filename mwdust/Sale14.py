###############################################################################
#
#   Sale14: extinction model from Sale et al. 2014 2014MNRAS.443.2907S
#
###############################################################################
import os, os.path
import sys
import tarfile
import shutil
import numpy
from scipy import interpolate
from astropy.io import ascii
from mwdust.util.extCurves import aebv
from mwdust.util.tools import cos_sphere_dist
from mwdust.util.download import downloader, dust_dir
from mwdust.DustMap3D import DustMap3D

_DEGTORAD= numpy.pi/180.
_saledir= os.path.join(dust_dir,'sale14')
_ERASESTR= "                                                                                "
class Sale14(DustMap3D):
    """extinction model from Sale et al. 2014 2014MNRAS.443.2907S"""
    def __init__(self,filter=None,sf10=True):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the Sale14 dust map
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
        OUTPUT:
           object
        HISTORY:
           2015-03-08 - Started - Bovy (IAS)
        """
        DustMap3D.__init__(self,filter=filter)
        self._sf10= sf10
        #Read the maps
        sys.stdout.write('\r'+"Reading Sale et al. (2014) data file ...\r")
        sys.stdout.flush()
        self._saledata= ascii.read(os.path.join(_saledir,
                                                     'Amap.dat'),
                                        readme=os.path.join(_saledir,
                                                            'ReadMe'),
                                        guess=False, format='cds',
                                        fill_values=[('', '-999')])
        sys.stdout.write('\r'+_ERASESTR+'\r')
        sys.stdout.flush()
        # Some summaries
        self._dl= self._saledata['lmax']-self._saledata['lmin']
        self._db= self._saledata['b_max']-self._saledata['b_min']
        self._lmin= numpy.amin(self._saledata['lmin'])
        self._lmax= numpy.amax(self._saledata['lmax'])
        self._bmin= numpy.amin(self._saledata['b_min'])
        self._bmax= numpy.amax(self._saledata['b_max'])
        self._ndistbin= 150
        self._ds= numpy.linspace(0.05,14.95,self._ndistbin)
        # For dust_vals
        self._sintheta= numpy.sin((90.-self._saledata['GLAT'])*_DEGTORAD)
        self._costheta= numpy.cos((90.-self._saledata['GLAT'])*_DEGTORAD)
        self._sinphi= numpy.sin(self._saledata['GLON']*_DEGTORAD)
        self._cosphi= numpy.cos(self._saledata['GLON']*_DEGTORAD)
        self._intps= numpy.zeros(len(self._saledata),dtype='object') #array to cache interpolated extinctions
        return None

    def _evaluate(self,l,b,d,_lbIndx=None):
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
           2015-03-08 - Started - Bovy (IAS)
        """
        if isinstance(l,numpy.ndarray) or isinstance(b,numpy.ndarray):
            raise NotImplementedError("array input for l and b for Sale et al. (2014) dust map not implemented")
        if _lbIndx is None: lbIndx= self._lbIndx(l,b)
        else: lbIndx= _lbIndx
        if self._intps[lbIndx] != 0:
            out= self._intps[lbIndx](d)
        else:
            tlbData= self.lbData(l,b)
            interpData=\
                interpolate.InterpolatedUnivariateSpline(self._ds,
                                                         tlbData['a0'],
                                                         k=1)
            out= interpData(d)
            self._intps[lbIndx]= interpData
        if self._filter is None: # Sale et al. say A0/Aks = 11
            return out/11./aebv('2MASS Ks',sf10=self._sf10)
        else: # if sf10, first put ebv on SFD scale
            return out/11./aebv('2MASS Ks',sf10=self._sf10)\
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
        indx= cos_sphere_dist(self._sintheta,self._costheta,
                              self._sinphi,self._cosphi,
                              numpy.sin((90.-bcen)*_DEGTORAD),
                              numpy.cos((90.-bcen)*_DEGTORAD),
                              numpy.sin(lcen*_DEGTORAD),
                              numpy.cos(lcen*_DEGTORAD)) \
                              >= numpy.cos(radius*_DEGTORAD)
        ll= self._saledata['GLON'][indx]
        bb= self._saledata['GLAT'][indx]
        # Now get the extinctions for these pixels
        pixarea= []
        extinction= []
        for l,b in zip(ll,bb):
            lbIndx= self._lbIndx(l,b)
            extinction.append(self._evaluate(l,b,dist,_lbIndx=lbIndx))
            pixarea.append(self._dl[lbIndx]*self._db[lbIndx]*_DEGTORAD**2.)
        pixarea= numpy.array(pixarea)
        extinction= numpy.array(extinction)
        return (pixarea,extinction)
               
    def dmax(self,l,b):
        """
        NAME:
           dmax
        PURPOSE:
           return the maximum distance for which to trust the Sale et al. (2014) data
        INPUT:
           l- Galactic longitude (deg)
           b- Galactic latitude (deg)
        OUTPUT:
           maximum distance in kpc
        HISTORY:
           2015-03-08 - Written - Bovy (IAS)
        """
        lbIndx= self._lbIndx(l,b)
        return self._saledata['trust'][lbIndx]/1000.

    def lbData(self,l,b):
        """
        NAME:
           lbData
        PURPOSE:
           return the Sale et al. (2014) data corresponding to a given
           line of sight
        INPUT:
           l- Galactic longitude (deg)
           b- Galactic latitude (deg)
        OUTPUT:
        HISTORY:
           2015-03-08 - Written - Bovy (IAS)
        """
        #Find correct entry
        lbIndx= self._lbIndx(l,b)
        #Build output array
        out= numpy.recarray((self._ndistbin,),
                            dtype=[('a0', 'f8'),
                                   ('e_a0','f8')])
        for ii in range(self._ndistbin):
            out[ii]['a0']= self._saledata[lbIndx]['meanA%i' % (ii+1)]
            out[ii]['e_a0']= self._saledata[lbIndx]['meanA%i' % (ii+1)]
        return out

    def _lbIndx(self,l,b):
        """Return the index in the _saledata array corresponding to this (l,b)"""
        if l <= self._lmin or l >= self._lmax \
                or b <= self._bmin or b >= self._bmax:
            raise IndexError("Given (l,b) pair not within the region covered by the Sale et al. (2014) dust map")
        return numpy.argmin((l-self._saledata['GLON'])**2./self._dl**2.\
                                +(b-self._saledata['GLAT'])**2./self._db**2.)

    @classmethod
    def download(cls, test=False):
        sale_folder_path = os.path.join(dust_dir, "sale14")
        sale_path = os.path.join(sale_folder_path, "Amap.tar.gz")
        if not os.path.exists(sale_path[:-6] + "dat"):
            if not os.path.exists(sale_folder_path):
                os.mkdir(sale_folder_path)
            _SALE_URL= "http://www.iphas.org/data/extinction/Amap.tar.gz"
            downloader(_SALE_URL, sale_path, cls.__name__, test=test)
            if not test:
                sale_file = tarfile.open(sale_path)
                sale_file.extractall(sale_folder_path)
                sale_file.close()
                os.remove(sale_path)
                # Fix one line in the dust map
                with open(os.path.join(sale_folder_path, "tmp.dat"), "w") as fout:
                    with open(os.path.join(sale_folder_path, "Amap.dat"), "r") as fin:
                        for line in fin:
                            if "15960.40000" in line: # bad line
                                newline= ''
                                for ii,word in enumerate(line.split(' ')):
                                    if ii > 0: newline+= ' '
                                    if ii > 6 and len(word) > 9:
                                        word= "747.91400"
                                    newline+= word
                                fout.write(newline+'\n')
                            else:
                                fout.write(line)
                shutil.move(os.path.join(sale_folder_path, "tmp.dat"), os.path.join(sale_folder_path, "Amap.dat"))
        return None
