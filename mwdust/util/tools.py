###############################################################################
#
#    mwutils.util.tools: some general tools
#
###############################################################################
import tqdm


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
       theta_o  - polar angle of center of the disk
       phi_o  - azimuth of the center of the disk
    OUTPUT:
       spherical distance
    HISTORY:
       2010-04-29 -Written - Bovy (NYU)
    """
    return (sintheta*sintheta_o
            *(cosphi_o*cosphi+
              sinphi_o*sinphi)+
            costheta_o*costheta)


class TqdmUpTo(tqdm.tqdm):
    """Provides `update_to(n)` which uses `tqdm.update(delta_n)`."""
    def update_to(self, b=1, bsize=1, tsize=None):
        """
        b  : int, optional
            Number of blocks transferred so far [default: 1].
        bsize  : int, optional
            Size of each block (in tqdm units) [default: 1].
        tsize  : int, optional
            Total size (in tqdm units). If [default: None] remains unchanged.
        """
        if tsize is not None:
            self.total = tsize
        self.update(b * bsize - self.n)  # will also set self.n = b * bsize
