import re
import os, os.path
import numpy

#A / E(B-v)
avebv=  {}
avebvsf= {}
def _read_extCurves():
    """Read the extinction curves files in extCurves"""
    extFile= open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'extCurves','extinction.tbl'),'r')
    global avebv
    global avebvsf
    for line in extFile:
        if line[0] == '\\': continue
        if line[0] == '|': continue
        vals= re.split('\s\s+',line)
        avebv[vals[0].strip()]= float(vals[4])
        avebvsf[vals[0].strip()]= float(vals[2])    
    # Add filters from Schlafly & Finkbeiner
    extFile= open(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                               'extCurves','apj398709t6_ascii.txt'),'r')
    cnt= 0
    for line in extFile:
        print line
        cnt+= 1
        if cnt < 6: continue
        if cnt > 49: break
        vals= line.split()
        # Each line has 2 filters
        filter1= '%s %s' % (vals[0],vals[1])
        if not filter1 in avebv:
            avebv[filter1]= numpy.nan
            avebvsf[filter1]= float(vals[4])
        filter2= '%s %s' % (vals[7],vals[8])
        if not filter2 in avebv:
            avebv[filter2]= numpy.nan
            avebvsf[filter2]= float(vals[11])

_read_extCurves()

def aebv(filter,sf10=True):
    """
    NAME:
       aebv
    PURPOSE:
       return A_filter / E(B-V), necessary to turn SFD E(B-V) into total extinctions
    INPUT:
       filter - filter to use (e.g., '2MASS Ks')
       sf10= (True) if True, use the values from Schlafly & Finkbeiner 2010, which use an updated extinction law, source spectrum, and recalibrated SFD map
    OUTPUT:
       A_filter / E(B-V)
    HISTORY:
       2013-11-24 - Written - Bovy (IAS)
    """
    if sf10:
        if not avebvsf.has_key(filter):
            raise ValueError("Requested filter is not supported")
        return avebvsf[filter]
    else:
        if not avebv.has_key(filter):
            raise ValueError("Requested filter is not supported")
        return avebv[filter]
