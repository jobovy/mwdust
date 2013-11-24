import re
import os, os.path

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

_read_extCurves()

def aebv(filter,sf10=True):
    """Return A_filter / E(B-V)"""
    if sf10:
        if not avebvsf.has_key(filter):
            raise ValueError("Requested filter is not supported")
        return avebvsf[filter]
    else:
        if not avebv.has_key(filter):
            raise ValueError("Requested filter is not supported")
        return avebv[filter]
