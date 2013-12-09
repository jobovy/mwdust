import os
from setuptools import setup
from distutils.core import Extension
import sys
import subprocess
import glob

longDescription= ""

#Download SFD maps
_DOWNLOAD_SFD= False
_SFD_URL_NGP= 'http://www.astro.princeton.edu/~schlegel/dust/dustpub/maps/SFD_dust_4096_ngp.fits'
_SFD_URL_SGP= 'http://www.astro.princeton.edu/~schlegel/dust/dustpub/maps/SFD_dust_4096_sgp.fits'
if _DOWNLOAD_SFD and sys.argv[1] in ('install'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        print '\033[1m'+'Downloading SFD dust maps ...'+'\033[0m'
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'maps',
                                           'SFD_dust_4096_ngp.fits')):
            if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'maps')):
                os.mkdir(os.path.join(os.getenv('DUST_DIR'),'maps'))
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
_DOWNLOAD_DRIMMEL= False
_DRIMMEL_URL= 'ftp://ftp.oato.inaf.it/astrometria/extinction/data-for.tar.gz'
if _DOWNLOAD_DRIMMEL \
        and sys.argv[1] in ('build','install','bdist','bdist_egg'):
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
_DOWNLOAD_MARSHALL= True
_MARSHALL_URL= 'ftp://cdsarc.u-strasbg.fr/pub/cats/J/A%2BA/453/635'
if _DOWNLOAD_MARSHALL and sys.argv[1] in ('install'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'marshall06')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'marshall06'))
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
                        'fortranfile'],
      ext_modules=ext_modules
      )
