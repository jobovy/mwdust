# combine_dustmaps.py: make a composite extinction map (Marshall,Green,Drimmel)
# Using legacy code and only runs in python 2
# Creates a composite map. Run from command line:
# python combine_dustmaps19.py combine19.sav (runs the combine_dustmap function)
# python combine_dustmaps19.py combine19.sav save (runs the store_h5 function)
# python combine_dustmaps19.py combine19.sav fixnans (runs the fix_nans function)
# The first call takes a few hours, can be tested via _DRYISHRUN = False first
###############################################################################
import sys
import os, os.path
import pickle
import numpy
import h5py
import healpy
import mwdust
from mwdust.util.download import dust_dir

from galpy.util import save_pickles


def distmod2dist(distmod):
    """distance modulus to distance in kpc"""
    return 10.**(distmod/5.-2.)

_greendir= os.path.join(dust_dir,'green19')
#_GREEN15DISTMODS= numpy.linspace(4.,19.,31) # distance spacing for green15 and green17
_GREEN19DISTMODS= numpy.linspace(4,18.875,120) # distance spacing for green19
_GREEN19DISTS= distmod2dist(_GREEN19DISTMODS)
_DEGTORAD= numpy.pi/180.
_ERASESTR= "                                                                                "
_DRYISHRUN= False
def combine_dustmap(picklename):
    if os.path.exists(picklename): return None
    ndists= len(_GREEN19DISTS)
    # First fill in with NSIDE = 512 for Marshall
    marshallmap= mwdust.Marshall06()
    nside_mar= 512
    mar_pix= numpy.arange(healpy.pixelfunc.nside2npix(nside_mar))
    mar_val= numpy.zeros((len(mar_pix),ndists))+healpy.UNSEEN
    theta, phi= \
        healpy.pixelfunc.pix2ang(nside_mar,mar_pix,nest=True)
    bb= (numpy.pi/2.-theta)/numpy.pi*180.
    ll= phi/numpy.pi*180.
    subIndx= (numpy.fabs(bb) < 10.125)\
        *((ll < 100.125)+(ll > 259.875))
    mar_pix= mar_pix[subIndx]
    mar_val= mar_val[subIndx]
    ll= ll[subIndx]
    ll[ll > 180.]-= 360.
    bb= bb[subIndx]
    for pp,dpix in enumerate(mar_pix):
        sys.stdout.write('\r'+"Working on pixel %i, %i remaining ...\r" % (pp+1,len(mar_pix)-pp))
        sys.stdout.flush()
        if _DRYISHRUN and pp > 100: break
        mar_val[pp]= marshallmap(ll[pp],bb[pp],_GREEN19DISTS)
    sys.stdout.write('\r'+_ERASESTR+'\r')
    sys.stdout.flush()
    # Now load Green19 and remove those pixels that fall within the Marshall map
    with h5py.File(os.path.join(_greendir,'bayestar2019.h5'),'r') as greendata:
        pix_info= greendata['/pixel_info'][:]
        best_fit= greendata['/best_fit'][:]
    # Check whether any of these fall within the Marshall map
    theta, phi= healpy.pixelfunc.pix2ang(pix_info['nside'].astype('int32'),
                                         pix_info['healpix_index'].astype('int64'),
                                         nest=True)
    inMar= ((phi < 100.125*_DEGTORAD)+(phi > 259.875*_DEGTORAD))\
        *(numpy.fabs(numpy.pi/2.-theta) < 10.125*_DEGTORAD)
    best_fit[inMar]= healpy.UNSEEN
    nside_min= numpy.min(pix_info['nside'])
    nside_max= numpy.max(pix_info['nside'])
    # Fill in remaining gaps with Drimmel at NSIDE=256
    pix_drim= []
    pix_drim_nside= []
    val_drim= []
    drimmelmap= mwdust.Drimmel03()   
    for nside_drim in 2**numpy.arange(8,int(numpy.log2(nside_max))+1,1):
        tpix= numpy.arange(healpy.pixelfunc.nside2npix(nside_drim))
        rmIndx= numpy.zeros(len(tpix),dtype='bool')
        # Remove pixels that already have values at this or a higher level
        for nside in 2**numpy.arange(8,
                                     int(numpy.log2(nside_max))+1,1):
            mult_factor = (nside/nside_drim)**2
            tgpix= pix_info['healpix_index'][pix_info['nside'] == nside]
            for offset in numpy.arange(mult_factor):
                rmIndx[numpy.in1d(tpix*mult_factor+offset,tgpix,
                                  assume_unique=True)]= True
        # Remove pixels that already have values at a lower level
        for nside in 2**numpy.arange(int(numpy.log2(nside_min)),
                                         int(numpy.log2(nside_drim)),1):
            mult_factor = (nside_drim/nside)**2
            # in Green 19
            tgpix= pix_info['healpix_index'][pix_info['nside'] == nside]
            rmIndx[numpy.in1d(tpix//mult_factor,tgpix,assume_unique=False)]= True
            # In the current Drimmel
            tdpix= numpy.array(pix_drim)[numpy.array(pix_drim_nside) == nside]
            rmIndx[numpy.in1d(tpix//mult_factor,tdpix,assume_unique=False)]= True
        # Also remove pixels that lie within the Marshall area
        theta, phi= healpy.pixelfunc.pix2ang(nside_drim,tpix,nest=True)
        inMar= ((phi < 100.125*_DEGTORAD)+(phi > 259.875*_DEGTORAD))\
            *(numpy.fabs(numpy.pi/2.-theta) < 10.125*_DEGTORAD)
        rmIndx[inMar]= True
        tpix= tpix[True-rmIndx]
        pix_drim.extend(tpix)
        pix_drim_nside.extend(nside_drim*numpy.ones(len(tpix)))
        ll= phi[True-rmIndx]/_DEGTORAD
        bb= (numpy.pi/2.-theta[True-rmIndx])/_DEGTORAD
        for pp in range(len(tpix)):
            sys.stdout.write('\r'+"Working on level %i, pixel %i, %i remaining ...\r" % (nside_drim,pp+1,len(tpix)-pp))
            sys.stdout.flush()
            val_drim.append(drimmelmap(ll[pp],bb[pp],_GREEN19DISTS))
            if _DRYISHRUN and pp > 1000: break
    sys.stdout.write('\r'+_ERASESTR+'\r')
    sys.stdout.flush()
    # Save
    g19Indx= best_fit[:,0] != healpy.UNSEEN
    save_pickles(picklename,mar_pix,mar_val,
                 pix_info['nside'][g19Indx],pix_info['healpix_index'][g19Indx],
                 best_fit[g19Indx],
                 pix_drim,pix_drim_nside,val_drim)
    return None

def store_h5(picklename):
    # Restore pickle
    if not os.path.exists(picklename):
        print("file %s does not exist!" % picklename)
        return None
    with open(picklename,'rb') as picklefile:
        mar_pix= pickle.load(picklefile)
        mar_val= pickle.load(picklefile)
        pix_info_nside= pickle.load(picklefile)
        pix_info_healpix= pickle.load(picklefile)
        best_fit= pickle.load(picklefile)
        pix_drim= pickle.load(picklefile)
        pix_drim_nside= pickle.load(picklefile)
        val_drim= pickle.load(picklefile)
    # Combine
    nout= len(mar_pix)+len(pix_info_nside)+len(val_drim)
    out_nside= numpy.empty(nout,dtype='uint32')
    out_healpix= numpy.empty(nout,dtype='uint64')
    out_bf= numpy.empty((nout,len(_GREEN19DISTS)),dtype='float64')
    # Load Marshall
    out_nside[:len(mar_pix)]= 512
    out_healpix[:len(mar_pix)]= mar_pix
    out_bf[:len(mar_pix)]= mar_val
    # Load Green 19
    out_nside[len(mar_pix):len(mar_pix)+len(pix_info_nside)]= pix_info_nside
    out_healpix[len(mar_pix):len(mar_pix)+len(pix_info_nside)]= pix_info_healpix
    out_bf[len(mar_pix):len(mar_pix)+len(pix_info_nside)]= best_fit
    # Load Drimmel
    if _DRYISHRUN:
        out_nside[len(mar_pix)+len(pix_info_nside):]= pix_drim_nside[:len(val_drim)]
        out_healpix[len(mar_pix)+len(pix_info_nside):]= pix_drim[:len(val_drim)]
    else:
        out_nside[len(mar_pix)+len(pix_info_nside):]= pix_drim_nside
        out_healpix[len(mar_pix)+len(pix_info_nside):]= pix_drim
    out_bf[len(mar_pix)+len(pix_info_nside):]= val_drim
    # Save to h5 file
    outfile= h5py.File(picklename.replace('.sav','.h5'),"w")
    pixinfo= numpy.recarray(len(out_nside),
                            dtype=[('nside','uint32'),
                                   ('healpix_index','uint64')])
    pixinfo['nside']= out_nside
    pixinfo['healpix_index']= out_healpix
    outfile.create_dataset("pixel_info", data=pixinfo)
    outfile.create_dataset("best_fit",data=out_bf)
    outfile.close()
    return None    

def fix_nans(picklename):
    """Marshall has a few NaNs, replace these with Drimmel"""
    with h5py.File(picklename.replace('.sav','.h5'),'r') as combdata:
        pix_info= combdata['/pixel_info'][:]
        best_fit= combdata['/best_fit'][:]
    nanIndx= numpy.isnan(best_fit[:,0])
    print("Found %i NaNs ..." % numpy.sum(nanIndx))
    theta, phi= healpy.pixelfunc.pix2ang(pix_info['nside'].astype('int32'),
                                         pix_info['healpix_index'].astype('int64'),
                                         nest=True)
    bb= (numpy.pi/2.-theta)/_DEGTORAD
    ll= phi/_DEGTORAD
    indices= numpy.arange(len(pix_info['nside']))[nanIndx]
    drimmelmap= mwdust.Drimmel03()   
    for ii in range(numpy.sum(nanIndx)):
        best_fit[indices[ii]]= drimmelmap(ll[ii],bb[ii],_GREEN19DISTS)
    # Now save
    nanIndx= numpy.isnan(best_fit[:,0])
    print("Found %i NaNs ..." % numpy.sum(nanIndx))
    # Save to h5 file
    outfile= h5py.File(picklename.replace('.sav','.h5'),"w")
    outfile.create_dataset("pixel_info", data=pix_info)
    outfile.create_dataset("best_fit",data=best_fit)
    outfile.close()
    return None

if __name__ == '__main__':
    if len(sys.argv) > 2 and sys.argv[2] == 'fixnans':
        fix_nans(sys.argv[1])
    elif len(sys.argv) > 2:
        store_h5(sys.argv[1])
    else:
        print(sys.argv[1])        
        combine_dustmap(sys.argv[1])
