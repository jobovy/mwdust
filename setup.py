import os
from setuptools import setup
from distutils.core import Extension
import sys
import subprocess
import glob

longDescription= ""

try:
    downloads_pos = sys.argv.index('--no-downloads')
except ValueError:
    _DOWNLOAD_SFD= True
    _DOWNLOAD_DRIMMEL= True
    _DOWNLOAD_MARSHALL= True
    _DOWNLOAD_SALE= True
    _DOWNLOAD_GREEN= True
    _DOWNLOAD_COMBINED= True
else:
    del sys.argv[downloads_pos]
    _DOWNLOAD_SFD= False
    _DOWNLOAD_DRIMMEL= False
    _DOWNLOAD_MARSHALL= False
    _DOWNLOAD_SALE= False
    _DOWNLOAD_GREEN= False
    _DOWNLOAD_COMBINED= False

#Download SFD maps
_SFD_URL_NGP= 'http://www.sdss3.org/svn/repo/catalogs/dust/trunk/maps/SFD_dust_4096_ngp.fits'
_SFD_URL_SGP= 'http://www.sdss3.org/svn/repo/catalogs/dust/trunk/maps/SFD_dust_4096_sgp.fits'
if _DOWNLOAD_SFD and sys.argv[1] in ('install','develop'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'maps',
                                           'SFD_dust_4096_ngp.fits')):
            if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'maps')):
                os.mkdir(os.path.join(os.getenv('DUST_DIR'),'maps'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'maps')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m'
            print '\033[1m'+'Downloading SFD dust maps ...'+'\033[0m'
            try:
                subprocess.check_call(['wget',_SFD_URL_NGP,'-O',
                                       os.path.join(os.getenv('DUST_DIR'),'maps',
                                                    'SFD_dust_4096_ngp.fits')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Downloading SFD dust-map data from %s failed ..." % _SFD_URL_NGP +'\033[0m'
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'maps',
                                                    'SFD_dust_4096_ngp.fits')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'maps',
                                           'SFD_dust_4096_sgp.fits')):
            try:
                subprocess.check_call(['wget',_SFD_URL_SGP,'-O',
                                       os.path.join(os.getenv('DUST_DIR'),'maps',
                                                    'SFD_dust_4096_sgp.fits')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Downloading SFD dust-map data from %s failed ..." % _SFD_URL_SGP +'\033[0m'
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'maps',
                                                    'SFD_dust_4096_sgp.fits')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'

#Download Drimmel data
_DRIMMEL_URL= 'ftp://ftp.oato.inaf.it/astrometria/extinction/data-for.tar.gz'
if _DOWNLOAD_DRIMMEL \
        and sys.argv[1] in ('build','install','develop','bdist','bdist_egg'):
    if not os.path.exists('mwdust/util/drimmeldata/data-for.tar.gz'):
        print '\033[1m'+'Downloading Drimmel et al. (2003) dust maps ...'+'\033[0m'
        try:
            subprocess.check_call(['wget','%s' % _DRIMMEL_URL,
                                   '-O','mwdust/util/drimmeldata/data-for.tar.gz'])
        except subprocess.CalledProcessError:
            print "Downloading Drimmel dust-map data from %s failed ..." % _DRIMMEL_URL
        try:
            subprocess.check_call(['tar','xvzf',
                                   'mwdust/util/drimmeldata/data-for.tar.gz',
                                   '-C','mwdust/util/drimmeldata/'])
        except subprocess.CalledProcessError:
            print "Untarring Drimmel dust-map data failed ..."

#Download Marshall data
_MARSHALL_URL= 'ftp://cdsarc.u-strasbg.fr/pub/cats/J/A%2BA/453/635'
if _DOWNLOAD_MARSHALL and sys.argv[1] in ('install','develop'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'marshall06')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'marshall06'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'marshall06')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m'
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'marshall06',
                                                'table1.dat')):
            print '\033[1m'+'Downloading Marshall et al. (2006) dust maps ...'+'\033[0m'
            try:
                subprocess.check_call(['wget',
                                       '%s/table1.dat.gz' % _MARSHALL_URL,
                                       '-O',
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'marshall06',
                                                    'table1.dat.gz')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Downloading Marshall dust-map data from %s/table1.dat.gz failed ..." % _MARSHALL_URL +'\033[0m'
            try:
                subprocess.check_call(['gunzip',
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'marshall06',
                                                    'table1.dat.gz')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Gunzipping Marshall et al. dust-map data failed ..."+'\033[0m'
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'marshall06',
                                                    'table1.dat')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'
            #Also download the ReadMe file
            try:
                subprocess.check_call(['wget','%s/ReadMe' % _MARSHALL_URL,
                                       '-O',
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'marshall06',
                                                    'ReadMe')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Downloading Marshall dust-map ReadMe from %s/ReadMe failed ..." % _MARSHALL_URL+'\033[0m'
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'marshall06',
                                                    'ReadMe')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'

#Download Sale data, currently unavailable from CDS
_SALE_CDS= False
if _SALE_CDS:
    _SALE_URL= 'ftp://cdsarc.u-strasbg.fr/pub/cats/J/MNRAS/443/2907'
else:
    _SALE_URL= 'http://www.iphas.org/data/extinction/Amap.tar.gz'
if _DOWNLOAD_SALE and sys.argv[1] in ('install','develop'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'sale14')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'sale14'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'sale14')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m'
        if not (os.path.exists(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                                'table1.dat')) 
                or os.path.exists(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                                'Amap.dat'))):
            print '\033[1m'+'Downloading Sale et al. (2014) dust maps ...'+'\033[0m'
            if _SALE_CDS:
                try:
                    subprocess.check_call(['wget',
                                           '%s/table1.dat.gz' % _SALE_URL,
                                           '-O',
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'table1.dat.gz')])
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Downloading Sale dust-map data from %s/table1.dat.gz failed ..." % _SALE_URL +'\033[0m'
                try:
                    subprocess.check_call(['gunzip',
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'table1.dat.gz')])
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Gunzipping Sale et al. dust-map data failed ..."+'\033[0m'
                try:
                    subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'table1.dat')])
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'
                #Also download the ReadMe file
                try:
                    subprocess.check_call(['wget','%s/ReadMe' % _SALE_URL,
                                           '-O',
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'ReadMe')])
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Downloading Sale dust-map ReadMe from %s/ReadMe failed ..." % _SALE_URL+'\033[0m'
                try:
                    subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'ReadMe')])
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'
            else:
                try:
                    subprocess.check_call(['wget',
                                           _SALE_URL,
                                           '-O',
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'Amap.tar.gz')])
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Downloading Sale dust-map data from %s failed ..." % _SALE_URL +'\033[0m'
                try:
                    subprocess.check_call(['tar','xvzf',
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'Amap.tar.gz'),
                                           '-C',
                                           os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14')])
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Untarring/unzipping Sale et al. dust-map data failed ..."+'\033[0m'
                try:
                    os.remove(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                           'Amap.tar.gz'))
                except subprocess.CalledProcessError:
                    print '\033[1m'+"Removing Sale et al. dust-map tarred data failed ..."+'\033[0m'
            # Fix one line in the dust map
            with open("tmp.dat", "w") as fout:
                with open(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                           'Amap.dat'),'r') as fin:
                    for line in fin:
                        if '15960.40000' in line: # bad line
                            newline= ''
                            for ii,word in enumerate(line.split(' ')):
                                if ii > 0: newline+= ' '
                                if ii > 6 and len(word) > 9:
                                    word= '747.91400'
                                newline+= word
                            fout.write(newline+'\n')
                        else:
                            fout.write(line)
            os.rename('tmp.dat',os.path.join(os.getenv('DUST_DIR'),'sale14',
                                             'Amap.dat'))

#Download Green et al. PanSTARRS data
_GREEN_URL= 'http://faun.rc.fas.harvard.edu/pan1/ggreen/argonaut/data/dust-map-3d.h5'
if _DOWNLOAD_GREEN and sys.argv[1] in ('install','develop'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'green15')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'green15'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'green15')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m'
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'green15',
                                           'dust-map-3d.h5')):
            print '\033[1m'+'Downloading Green et al. (2015) dust maps ...'+'\033[0m'
            try:
                subprocess.check_call(['wget',
                                       _GREEN_URL,
                                       '-O',
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'green15',
                                                    'dust-map-3d.h5')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Downloading Green dust-map data from %s failed ..." % _GREEN_URL +'\033[0m'
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'green15',
                                                    'dust-map-3d.h5')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'

#Download the combined map of Bovy et al. (2015): Marshall+Green+Drimmel for full sky coverage
_COMBINED_URL= 'http://TBD'
if _DOWNLOAD_COMBINED and sys.argv[1] in ('install','develop'):
    print '\033[1m'+'Downloading combined dust map failed, as it is currently unavailable; contact Bovy for access ...'+'\033[0m'
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'combined15')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'combined15'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'combined15')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m'
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'combined15',
                                           'dust-map-3d.h5')):
            print '\033[1m'+'Downloading combined dust map (2015) ...'+'\033[0m'
            try:
                subprocess.check_call(['wget',
                                       _COMBINED_URL,
                                       '-O',
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'combined15',
                                                    'dust-map-3d.h5')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Downloading combined dust-map data from %s failed ..." % _COMBINED_URL +'\033[0m'
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'combined15',
                                                    'dust-map-3d.h5')])
            except subprocess.CalledProcessError:
                print '\033[1m'+"Problem changing ownership of data file..."+'\033[0m'

#SFD  extension
sfd_c_src= glob.glob('mwdust/util/SFD_CodeC/*.c')

sfd_libraries=['m']
sfd_c= Extension('sfd_c',
                 sources=sfd_c_src,
                 libraries=sfd_libraries,
                 extra_compile_args=['-DLITTLE_ENDIAN'],
                 include_dirs=['mwdust/util/SFD_CodeC'])

ext_modules=[sfd_c]

setup(name='mwdust',
      version='1.',
      description='Dust in the Milky Way',
      author='Jo Bovy',
      author_email='bovy@ias.edu',
      license='New BSD',
      long_description=longDescription,
      url='https://github.com/jobovy/mwdust',
      package_dir = {'mwdust/': ''},
      packages=['mwdust',
                'mwdust/util'],
      package_data={'mwdust/util':['extCurves/extinction.tbl',
                                   'drimmeldata/*.dat']},
      install_requires=['numpy','scipy','matplotlib','asciitable',
                        'fortranfile','h5py','healpy'],
      ext_modules=ext_modules,
      classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python :: 2.7",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"]
      )
