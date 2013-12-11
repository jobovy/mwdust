###############################################################################
#
#   DustMap3D: top-level class for a 3D dust map; all other dust maps inherit
#              from this
#
###############################################################################
import numpy
try:
    from galpy.util import bovy_plot
    _BOVY_PLOT_LOADED= True
except ImportError:
    _BOVY_PLOT_LOADED= False
class DustMap3D:
    """top-level class for a 3D dust map; all other dust maps inherit from this"""
    def __init__(self,filter=None):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the dust map
        INPUT:
           filter= filter to return the extinction in when called
        OUTPUT:
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        self._filter= filter
        return None

    def __call__(self,*args,**kwargs):
        """
        NAME:
           __call__
        PURPOSE:
           evaluate the dust map
        INPUT:
           Either:
              (l,b,d) -  Galactic longitude, latitude (deg), and distance (kpc)
        OUTPUT:
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        if True: #(l,b,d)
            l,b,d= args
            if isinstance(d,(int,float,numpy.float32,numpy.float64)):
                d= numpy.array([d])
            try:
                return self._evaluate(l,b,d,**kwargs)
            except AttributeError:
                raise
                raise NotImplementedError("'_evaluate' for this DustMap3D not implemented yet")

    def plot(self,l,b,*args,**kwargs):
        """
        NAME:
           plot
        PURPOSE:
           plot the extinction along a given line of sight as a function of 
           distance
        INPUT:
           l,b - Galactic longitude and latitude (degree)
           range= distance range in kpc
           bovy_plot.bovy_plot args and kwargs
        OUTPUT:
           plot to output device
        HISTORY:
           2013-12-11 - Written - Bovy (IAS)
        """
        if not _BOVY_PLOT_LOADED:
            raise NotImplementedError("galpy.util.bovy_plot could not be loaded, so there is no plotting; might have to install galpy (http://github.com/jobovy/galpy) for plotting")
        if kwargs.has_key('range'):
            range= kwargs['range']
            kwargs.pop('range')
        else:
            range= [0.,12.]
        if kwargs.has_key('nds'):
            nds= kwargs['nds']
            kwargs.pop('nds')
        else:
            nds= 101
        #First evaluate the dust map
        ds= numpy.linspace(range[0],range[1],nds)
        adust= self(l,b,ds)
        #Add labels
        kwargs['xlabel']= r'$D\,(\mathrm{kpc})$'
        kwargs['ylabel']= r'$A_{%s}\,(\mathrm{mag})$' % (self._filter.split(' ')[-1])
        return bovy_plot.bovy_plot(ds,adust,*args,**kwargs)
