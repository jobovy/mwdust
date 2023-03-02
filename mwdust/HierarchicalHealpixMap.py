###############################################################################
#
#   HierarchicalHealpixMap: General class for extinction maps given as
#                           a hierarchical HEALPix pixelation (e.g., Green
#                           et al. 2015)
#
###############################################################################
import numpy
from scipy import interpolate
from mwdust.util.healpix import ang2pix
from mwdust.util.extCurves import aebv
from mwdust.DustMap3D import DustMap3D
_DEGTORAD= numpy.pi/180.
class HierarchicalHealpixMap(DustMap3D):
    """General class for extinction maps given as a hierarchical HEALPix 
    pixelation (e.g., Green et al. 2015) """
    def __init__(self,filter=None,sf10=True):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the combined dust map
        INPUT:
           filter= filter to return the extinction in
           sf10= (True) if True, use the Schlafly & Finkbeiner calibrations
        OUTPUT:
           object
        HISTORY:
           2015-07-28 - Started - Bovy (UofT)
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
           2015-03-02 - Started - Bovy (IAS)
        """
        distmod= 5.*numpy.log10(d)+10.
        if isinstance(l,numpy.ndarray) or isinstance(b,numpy.ndarray):
            raise NotImplementedError("array input for l and b for combined dust map not implemented")
        lbIndx= self._lbIndx(l,b)
        if self._intps[lbIndx] != 0:
            out= self._intps[lbIndx][0](distmod)
        else:
            interpData=\
                interpolate.InterpolatedUnivariateSpline(self._distmods,
                                                         self._best_fit[lbIndx],
                                                         k=self._interpk)
            out= interpData(distmod)
            self._intps[lbIndx]= interpData
        if self._filter is None:
            return out
        else:
            return out*aebv(self._filter,sf10=self._sf10)

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
        try:
            import healpy
        except ImportError:
            raise ModuleNotFoundError("This function requires healpy to be installed")
        # Convert the disk center to a HEALPIX vector
        vec= healpy.pixelfunc.ang2vec((90.-bcen)*_DEGTORAD,lcen*_DEGTORAD)
        distmod= 5.*numpy.log10(dist)+10.
        # Query the HEALPIX map for pixels that lie within the disk
        pixarea= []
        extinction= []
        for nside in self._nsides:
            # Find the pixels at this resolution that fall within the disk
            ipixs= healpy.query_disc(nside,vec,radius*_DEGTORAD,
                                    inclusive=False,nest=True)
            # Get indices of all pixels within the disk at current nside level
            nsideindx= self._pix_info['nside'] == nside
            potenIndxs= self._indexArray[nsideindx]
            nsidepix= self._pix_info['healpix_index'][nsideindx]
            # Loop through the pixels in the (small) disk
            tout= []
            for ii,ipix in enumerate(ipixs):
                lbIndx= potenIndxs[ipix == nsidepix]
                if numpy.sum(lbIndx) == 0: continue
                if self._intps[lbIndx] != 0:
                    tout.append(self._intps[lbIndx][0](distmod))
                else:
                    interpData=\
                        interpolate.InterpolatedUnivariateSpline(self._distmods,
                                                                 self._best_fit[lbIndx],
                                                                 k=self._interpk)
                    tout.append(interpData(distmod))
                    self._intps[lbIndx]= interpData
            tarea= healpy.pixelfunc.nside2pixarea(nside)
            tarea= [tarea for ii in range(len(tout))]
            pixarea.extend(tarea)
            extinction.extend(tout)
        pixarea= numpy.array(pixarea)
        extinction= numpy.array(extinction)
        if not self._filter is None:
            extinction= extinction*aebv(self._filter,sf10=self._sf10)        
        return (pixarea,extinction)

    def _lbIndx(self,l,b):
        """Return the index in the _combineddata array corresponding to this (l,b)"""
        for nside in self._nsides:
            # Search for the pixel in this Nside level
            tpix= ang2pix(nside,(90.-b)*_DEGTORAD,
                                           l*_DEGTORAD,nest=True)
            indx= (self._pix_info['healpix_index'] == tpix)\
                *(self._pix_info['nside'] == nside)
            if numpy.sum(indx) == 1:
                return self._indexArray[indx]
            elif numpy.sum(indx) > 1:
                raise IndexError("Given (l,b) pair has multiple matches!")
        raise IndexError("Given (l,b) pair not within the region covered by the extinction map")

    def plot_mollweide(self,d,**kwargs):
        """
        NAME:
           plot_mollweide
        PURPOSE:
           plot the extinction across the sky in Galactic coordinates  out to a given distance using a Mollweide projection
        INPUT:
           d - distance in kpc (nearest distance to this in the map is plotted)
           nside_plot= (2048) nside of the plotted map
           healpy.visufunc.mollview kwargs
        OUTPUT:
           plot to output device
        HISTORY:
           2019-12-06 - Written - Bovy (UofT)
        """
        try:
            import healpy
        except ImportError:
            raise ModuleNotFoundError("This function requires healpy to be installed")
        # Distance modulus
        dm= 5.*numpy.log10(d)+10.
        # Get factor to apply to map to obtain extinction in object's filter
        filter_fac= aebv(self._filter,sf10=self._sf10) \
                    if not self._filter is None else 1.
        # Map the dust map to a common nside, first find nearest distance pixel
        tpix= numpy.argmin(numpy.fabs(dm-self._distmods))
        # Construct an empty map at the highest HEALPix resolution present in the map; code snippets adapted from http://argonaut.skymaps.info/usage
        nside_max= numpy.max(self._pix_info['nside'])
        npix= healpy.pixelfunc.nside2npix(nside_max)
        pix_val= numpy.empty(npix,dtype='f8')
        pix_val[:] = healpy.UNSEEN
        # Fill the upsampled map
        for nside in numpy.unique(self._pix_info['nside']):
            # Get indices of all pixels at current nside level
            indx= self._pix_info['nside'] == nside
            # Extract A_X of each selected pixel
            pix_val_n= filter_fac*self._best_fit[indx,tpix]
            # Determine nested index of each selected pixel in upsampled map
            mult_factor = (nside_max//nside)**2
            pix_idx_n = self._pix_info['healpix_index'][indx]*mult_factor
            # Write the selected pixels into the upsampled map
            for offset in range(mult_factor):
                pix_val[pix_idx_n+offset] = pix_val_n[:]
        # If the desired nside is less than the maximum nside in the map, degrade
        nside_plot= kwargs.get('nside_plot',2048)
        if not nside_plot is None and nside_plot < nside_max:
            pix_val= healpy.pixelfunc.ud_grade(pix_val,
                                               nside_plot,pess=False,
                                               order_in='NEST', 
                                               order_out='NEST')
        pix_val[pix_val == healpy.UNSEEN]= -1.

        if not self._filter is None:
            kwargs['unit']= r'$A_{%s}\,(\mathrm{mag})$' % (self._filter.split(' ')[-1])
        else:
            kwargs['unit']= r'$E(B-V)\,(\mathrm{mag})$'
        kwargs['title']= kwargs.get('title',"")
        healpy.visufunc.mollview(pix_val,
                                 nest=True,
                                 xsize=4000,
                                 min=0.,
                                 max=numpy.quantile(pix_val,0.99),
                                 format=r'$%g$',
                                 cmap='gist_yarg',
                                 **kwargs)
        return None