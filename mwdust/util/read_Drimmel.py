import os, os.path
import fortranfile
_DRIMMELDIR= os.path.join(os.path.dirname(os.path.realpath(__file__)),
                          'drimmeldata')
def readDrimmelAll():
    out= {}
    allFilenames= ['avgrid.dat','avori2.dat','rf_allsky.dat',
               'avdisk.dat','avloc.dat','avspir.dat',
               'avdloc.dat','avori.dat']
    for filename in allFilenames:
        f = fortranfile.FortranFile(os.path.join(_DRIMMELDIR,filename))
        nx, ny, nz= 151, 151, 51
        if 'avori2' in filename:
            nx, ny, nz= 101, 201, 51
        elif 'avori' in filename:
            nx, ny, nz= 76, 151, 51
        elif 'avloc' in filename:
            nx, ny, nz= 101, 201, 51
        elif 'avdloc' in filename:
            nx, ny, nz= 31, 31, 51
        print filename, nx, ny, nz
        if 'rf_allsky' in filename:
            out[filename.split('.')[0]]= f.readReals()
        else:
            out[filename.split('.')[0]]= f.readReals().reshape((nz,ny,nx)).T
    return out
