###############################################################################
#
#   Drimmel03: extinction model from Drimmel et al. 2003 2003A&A...409..205D
#
###############################################################################
import copy
import numpy
from scipy.ndimage import map_coordinates
from scipy import optimize
try:
    import healpy
except ImportError: pass
from mwdust.util.extCurves import aebv
from mwdust.util import read_Drimmel
from mwdust.util.tools import cos_sphere_dist
from mwdust.DustMap3D import DustMap3D
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
        #Various setups
        self._xsun= -8.
        self._zsun= 0.015
        #Global grids
        self._nx_disk, self._ny_disk, self._nz_disk= 151, 151, 51
        self._dx_disk, self._dy_disk, self._dz_disk= 0.2, 0.2, 0.02
        self._nx_ori, self._ny_ori, self._nz_ori= 76, 151, 51
        self._dx_ori, self._dy_ori, self._dz_ori= 0.05, 0.05, 0.02
        #Local grids
        self._nx_diskloc, self._ny_diskloc, self._nz_diskloc= 31, 31, 51
        self._dx_diskloc, self._dy_diskloc, self._dz_diskloc= 0.05, 0.05, 0.02
        self._nx_ori2, self._ny_ori2, self._nz_ori2= 101, 201, 51
        self._dx_ori2, self._dy_ori2, self._dz_ori2= 0.02, 0.02, 0.02
        return None

    def _evaluate(self,l,b,d,norescale=False,
                  _fd=1.,_fs=1.,_fo=1.):
        """
        NAME:
           _evaluate
        PURPOSE:
           evaluate the dust-map
        INPUT:
           l- Galactic longitude (deg)
           b- Galactic latitude (deg)
           d- distance (kpc) can be array
           norescale= (False) if True, don't apply re-scalings
           _fd, _fs, _fo= (1.) amplitudes of the different components
        OUTPUT:
           extinction
        HISTORY:
           2013-12-10 - Started - Bovy (IAS)
        """
        if isinstance(l,numpy.ndarray) or isinstance(b,numpy.ndarray):
            raise NotImplementedError("array input for l and b for Drimmel dust map not implemented")

        cl= numpy.cos(l*_DEGTORAD)
        sl= numpy.sin(l*_DEGTORAD)
        cb= numpy.cos(b*_DEGTORAD)
        sb= numpy.sin(b*_DEGTORAD)

        #Setup arrays
        avori= numpy.zeros_like(d)
        avspir= numpy.zeros_like(d)
        avdisk= numpy.zeros_like(d)

        #Find nearest pixel in COBE map for the re-scaling
        rfIndx= numpy.argmax(cos_sphere_dist(self._rf_sintheta,
                                             self._rf_costheta,
                                             self._rf_sinphi,
                                             self._rf_cosphi,
                                             numpy.sin(numpy.pi/2.-b*_DEGTORAD),
                                             numpy.cos(numpy.pi/2.-b*_DEGTORAD),
                                             sl,cl))

        rfdisk, rfspir, rfori= 1., 1., 1,
        if self._drimmelMaps['rf_comp'][rfIndx] == 1 and not norescale:
            rfdisk= self._drimmelMaps['rf'][rfIndx]
        elif self._drimmelMaps['rf_comp'][rfIndx] == 2 and not norescale:
            rfspir= self._drimmelMaps['rf'][rfIndx]
        elif self._drimmelMaps['rf_comp'][rfIndx] == 3 and not norescale:
            rfori= self._drimmelMaps['rf'][rfIndx]

        #Find maximum distance
        dmax= 100.
        if b != 0.: dmax= .49999/numpy.fabs(sb) - self._zsun/sb
        if cl != 0.:
            tdmax= (14.9999/numpy.fabs(cl)-self._xsun/cl)
            if tdmax < dmax: dmax= tdmax
        if sl != 0.:
            tdmax = 14.9999/numpy.fabs(sl)
            if tdmax < dmax: dmax= tdmax
        d= copy.copy(d)
        d[d > dmax]= dmax
        
        #Rectangular coordinates
        X= d*cb*cl
        Y= d*cb*sl
        Z= d*sb+self._zsun

        #Local grid
        #Orion
        locIndx= (numpy.fabs(X) < 1.)*(numpy.fabs(Y) < 2.)
        if numpy.sum(locIndx) > 0:
            xi = X[locIndx]/self._dx_ori2+float(self._nx_ori2-1)/2.
            yj = Y[locIndx]/self._dy_ori2+float(self._ny_ori2-1)/2.
            zk = Z[locIndx]/self._dz_ori2+float(self._nz_ori2-1)/2.
            avori[locIndx]= map_coordinates(self._drimmelMaps['avori2'],
                                            [xi,yj,zk],
                                            mode='constant',cval=0.)
        #local disk
        locIndx= (numpy.fabs(X) < 0.75)*(numpy.fabs(Y) < 0.75)
        if numpy.sum(locIndx) > 0:
            xi = X[locIndx]/self._dx_diskloc+float(self._nx_diskloc-1)/2.
            yj = Y[locIndx]/self._dy_diskloc+float(self._ny_diskloc-1)/2.
            zk = Z[locIndx]/self._dz_diskloc+float(self._nz_diskloc-1)/2.
            avdisk[locIndx]= map_coordinates(self._drimmelMaps['avdloc'],
                                             [xi,yj,zk],
                                             mode='constant',cval=0.)
        
        #Go to Galactocentric coordinates
        X= X+self._xsun

        #Stars beyond the local grid
        #Orion
        globIndx= True-(numpy.fabs(X-self._xsun) < 1.)*(numpy.fabs(Y) < 2.)
        if numpy.sum(globIndx) > 0:
            #Orion grid is different from other global grids, so has its own dmax
            dmax= 100.
            if b != 0.: dmax= .49999/numpy.fabs(sb) - self._zsun/sb
            if cl > 0.:
                tdmax = (2.374999/numpy.fabs(cl))
                if tdmax < dmax: dmax= tdmax
            if cl < 0.:
                tdmax = (1.374999/numpy.fabs(cl))
                if tdmax < dmax: dmax= tdmax
            if sl != 0.:
                tdmax = (3.749999/numpy.fabs(sl))
                if tdmax < dmax: dmax= tdmax
            dori= copy.copy(d)
            dori[dori > dmax]= dmax
            Xori= dori*cb*cl+self._xsun
            Yori= dori*cb*sl
            Zori= dori*sb+self._zsun

            xi = Xori[globIndx]/self._dx_ori + 2.5*float(self._nx_ori-1)
            yj = Yori[globIndx]/self._dy_ori + float(self._ny_ori-1)/2.
            zk = Zori[globIndx]/self._dz_ori + float(self._nz_ori-1)/2.

            avori[globIndx]= map_coordinates(self._drimmelMaps['avori'],
                                             [xi,yj,zk],
                                             mode='constant',cval=0.)
        #disk & spir
        xi = X/self._dx_disk+float(self._nx_disk-1)/2.
        yj = Y/self._dy_disk+float(self._ny_disk-1)/2.
        zk = Z/self._dz_disk+float(self._nz_disk-1)/2.
        avspir= map_coordinates(self._drimmelMaps['avspir'],
                                [xi,yj,zk],
                                mode='constant',cval=0.)
        globIndx= True-(numpy.fabs(X-self._xsun) < 0.75)*(numpy.fabs(Y) < 0.75)
        if numpy.sum(globIndx) > 0:
            avdisk[globIndx]= map_coordinates(self._drimmelMaps['avdisk'],
                                              [xi,yj,zk],
                                              mode='constant',
                                              cval=0.)[globIndx]
        
        #Return
        out=_fd*rfdisk*avdisk+_fs*rfspir*avspir+_fo*rfori*avori
        if self._filter is None: # From Rieke & Lebovksy (1985); if sf10, first put ebv on SFD scale
            return out/3.09/((1-self._sf10)+self._sf10*0.86)
        else: 
            return out/3.09/((1-self._sf10)+self._sf10*0.86)\
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
        # Convert the disk center to a HEALPIX vector
        vec= healpy.pixelfunc.ang2vec((90.-bcen)*_DEGTORAD,lcen*_DEGTORAD)
        # We pixelize the map with a HEALPIX grid with nside=256, to somewhat
        # oversample the Drimmel resolution
        nside= 256
        # Find the pixels at this resolution that fall within the disk
        ipixs= healpy.query_disc(nside,vec,radius*_DEGTORAD,
                                 inclusive=False,nest=False)
        # Query the HEALPIX map for pixels that lie within the disk
        pixarea= healpy.pixelfunc.nside2pixarea(nside)+numpy.zeros(len(ipixs))
        extinction= []
        for ii, ipix in enumerate(ipixs):
            # Get glon and glat
            b9, l= healpy.pixelfunc.pix2ang(nside,ipix,nest=False)
            b= 90.-b9/_DEGTORAD
            l/= _DEGTORAD
            # Now evaluate
            extinction.append(self._evaluate(l,b,dist))
        extinction= numpy.array(extinction)
        return (pixarea,extinction)

    def fit(self,l,b,dist,ext,e_ext):
        """
        NAME:
           fit
        PURPOSE:
           fit the amplitudes of the disk, spiral, and Orion parts of the
           Drimmel map to other data
        INPUT:
           l,b- Galactic longitude and latitude in degree
           dist - distance in kpc
           ext - extinction at dist
           e_ext - error in extinction
        OUTPUT:
           (fd,fs,fo,dist_stretch) amplitudes of disk, spiral, and Orion parts
           and a 'distance stretch' applied to the model
           (applied as self(l,b,dist*dist_stretch))
        HISTORY:
           2013-12-16 - Written - Bovy (IAS)
        """
        #Fit consists of 
        #a) overall amplitude A
        #b) relative amplitude fd/A, fs/A
        #c) distance stretch
        pars= numpy.array([0.,numpy.log(1./3.),numpy.log(1./3.),0.])
        pars=\
            optimize.fmin_powell(_fitFunc,pars,args=(self,l,b,dist,ext,e_ext))
        amp= numpy.exp(pars[0])
        fd= amp*numpy.exp(pars[1])
        fs= amp*numpy.exp(pars[2])
        fo= amp*(1.-fd-fs)
        return (fd,fs,fo,numpy.exp(pars[3]))
        
def _fitFunc(pars,drim,l,b,dist,ext,e_ext):
    amp= numpy.exp(pars[0])
    fd= amp*numpy.exp(pars[1])
    fs= amp*numpy.exp(pars[2])
    fo= amp*(1.-fd-fs)
    dist_stretch= numpy.exp(pars[3])
    model_ext= drim(l,b,dist*dist_stretch,_fd=fd,_fs=fs,_fo=fo)
    return 0.5*numpy.sum((model_ext-ext)**2./e_ext**2.)
    
