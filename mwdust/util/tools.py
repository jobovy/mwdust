###############################################################################
#
#    mwutils.util.tools: some general tools
#
###############################################################################
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
