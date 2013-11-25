###############################################################################
#
#   DustMap3D: top-level class for a 3D dust map; all other dust maps inherit
#              from this
#
###############################################################################
class DustMap3D:
    """top-level class for a 3D dust map; all other dust maps inherit from this"""
    def __init__(self):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the dust map
        INPUT:
        OUTPUT:
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        return None

    def __call__(self,*args,**kwargs):
        """
        NAME:
           __call__
        PURPOSE:
           evaluate the dust map
        INPUT:
        OUTPUT:
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        raise NotImplementedError("'__call__' for this DustMap3D not implemented yet")

