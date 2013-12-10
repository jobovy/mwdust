import os, os.path
import numpy
import struct
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
        if not 'rf_allsky' in filename:
            out[filename.split('.')[0]]=\
                f.readReals(prec='f').reshape((nz,ny,nx)).T
        else:
            #Need to do more work to read this file
            rec= f._read_exactly(4) #Read the header
            rec= f._read_exactly(4*393216)
            num = len(rec)/struct.calcsize('i')
            out_rf_pixnum= numpy.array(struct.unpack(f.ENDIAN+str(num)+'i',
                                                     rec),dtype='int')
            rec= f._read_exactly(4*393216)
            num = len(rec)/struct.calcsize('i')
            out_rf_comp= numpy.array(struct.unpack(f.ENDIAN+str(num)+'i',
                                                   rec),dtype='int')
            rec= f._read_exactly(4*393216)
            num = len(rec)/struct.calcsize('f')
            out_rf_glon= numpy.array(struct.unpack(f.ENDIAN+str(num)+'f',
                                                   rec),dtype=numpy.float32)
            rec= f._read_exactly(4*393216)
            num = len(rec)/struct.calcsize('f')
            out_rf_glat= numpy.array(struct.unpack(f.ENDIAN+str(num)+'f',
                                                   rec),dtype=numpy.float32)
            rec= f._read_exactly(4*393216)
            num = len(rec)/struct.calcsize('f')
            out_rf= numpy.array(struct.unpack(f.ENDIAN+str(num)+'f',
                                              rec),dtype=numpy.float32)
            out['rf_pixnum']= out_rf_pixnum
            out['rf_comp']= out_rf_comp
            out['rf_glon']= out_rf_glon
            out['rf_glat']= out_rf_glat
            out['rf']= out_rf
        f.close()
    return out
