###############################################################################
#
#   DustMap3D: top-level class for a 3D dust map; all other dust maps inherit
#              from this
#
###############################################################################
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
            try:
                return self._evaluate(*args,**kwargs)
            except AttributeError:
                raise
                raise NotImplementedError("'_evaluate' for this DustMap3D not implemented yet")
