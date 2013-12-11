###############################################################################
#
#   Drimmel03: extinction model from Drimmel et al. 2003 2003A&A...409..205D
#
###############################################################################
import copy
import numpy
from scipy.ndimage import map_coordinates
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
           norescale= (False) if True, don't apply re-scalings
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
        out=rfdisk*avdisk+rfspir*avspir+rfori*avori
        if self._filter is None:
            return out/3.09 #From Rieke & Lebovksy (1985)
        else:
            return out/3.09\
                *aebv(self._filter,sf10=self._sf10)

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
