import os
from setuptools import setup
from distutils.core import Extension
import sys
import subprocess
import glob

longDescription= ""

#Download Drimmel data first
_DOWNLOAD_DRIMMEL= False
_DRIMMEL_URL= 'ftp://ftp.oato.inaf.it/astrometria/extinction/data-for.tar.gz'
if _DOWNLOAD_DRIMMEL \
        and sys.argv[1] in ('build','install','bdist','bdist_egg'):
    if not os.path.exists('mwdust/util/drimmeldata/data-for.tar.gz'):
        try:
            subprocess.check_call(['wget','%s' % _DRIMMEL_URL,
                                   '-O','mwdust/util/drimmeldata/data-for.tar.gz'])
        except subprocess.CalledProcessError:
            print "Downloading Drimmel dust-map data from %s failed ..." % _DRIMMEL_URL
            raise
        try:
            subprocess.check_call(['tar','xvzf',
                                   'mwdust/util/drimmeldata/data-for.tar.gz',
                                   '-C','mwdust/util/drimmeldata/'])
        except subprocess.CalledProcessError:
            print "Untarring Drimmel dust-map data failed ..."

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
