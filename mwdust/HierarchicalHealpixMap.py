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
    def __init__(self,filter=None,sf10=True, **download_kwargs):
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
        super(HierarchicalHealpixMap, self).__init__(filter=filter, **download_kwargs)
        self._sf10 = sf10
        return None


    def _evaluate(self, ls, bs, ds):
        """
        NAME:
           _evaluate
        PURPOSE:
           evaluate the dust-map for array input
        INPUT:
           l- Galactic longitude (deg) can be array
           b- Galactic latitude (deg) can be array
           d- distance (kpc) can be array
        OUTPUT:
           extinction E(B-V)
        HISTORY:
           2015-03-02 - Started - Bovy (IAS)
           2023-07-05 - Vectorized - Henry Leung (UofT)
        """
        ls = numpy.atleast_1d(ls)
        bs = numpy.atleast_1d(bs)
        ds = numpy.atleast_1d(ds)

        distmod= 5.*numpy.log10(ds)+10.
        lbIndx= self._lbIndx(ls, bs)
        if len(ls) == 1 and len(ds) > 1:
            lbIndx = numpy.tile(lbIndx, len(ds))

        result = numpy.zeros_like(ds)
        for counter, i, d in zip(numpy.arange(len(result)), lbIndx, distmod):
            if self._intps[i] != 0:
                out= self._intps[i](d)
            else:
                interpData=\
                    interpolate.InterpolatedUnivariateSpline(self._distmods,
                                                            self._best_fit[i],
                                                            k=self._interpk)
                out= interpData(d)
                self._intps[i]= interpData
            result[counter] = out
        if self._filter is not None:
            result =  result * aebv(self._filter,sf10=self._sf10)
        # set nan for invalid indices
        result[lbIndx==-1] = numpy.nan
        return result


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

    def _lbIndx(self, ls, bs):
        """Return the indices in the _combineddata array corresponding to arrays of (l, b)"""
        stop_mask = numpy.zeros(len(ls), dtype=bool)  # mask to be accumulated when looping through nside
        indx_result = numpy.ones(len(ls), dtype=int) * -1  # -1 for bad star, int array has no nan
        for nside in self._nsides:
            tpix = ang2pix(nside, (90.-bs)*_DEGTORAD, ls*_DEGTORAD, nest=True)
            nside_idx = numpy.where(self._pix_info['nside'] == nside)[0]
            healpix_index_nside = self._pix_info['healpix_index'][nside_idx]
            sorted_order = numpy.argsort(healpix_index_nside)
            # use searchsorted to find the index of tpix in healpix_index_nside efficiently
            result = numpy.searchsorted(healpix_index_nside, tpix, sorter=sorted_order)
            # need to deal with indices where they are larger than the largest healpix_index_nside
            known_bad_idx = (result == len(nside_idx))
            result[known_bad_idx] = 0  # wrap around
            result = sorted_order[result]  # reverse the sorting before indexing
            result = nside_idx[result]
            good_result_idx = ((self._pix_info['healpix_index'][result] == tpix) & (self._pix_info['nside'][result] == nside) & (~known_bad_idx))
            indx_result = numpy.where(~stop_mask & good_result_idx, result, indx_result)
            indx_result = numpy.where(known_bad_idx & ~stop_mask, -1, indx_result)  # set bad star to -1
            stop_mask = stop_mask | good_result_idx  # update mask for the next nside
        return indx_result

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
