import os
import shutil
from setuptools import setup
from distutils.core import Extension
import sys
import subprocess
import glob
import platform
WIN32= platform.system() == 'Windows'

long_description= ''
previous_line= ''
with open('README.rst') as dfile:
    for line in dfile:
        if not 'image' in line and not 'target' in line \
                and not 'DETAILED' in line and not '**master**' in line \
                and not '**development' in line \
                and not 'DETAILED' in  previous_line:
            long_description+= line
        previous_line= line

#SFD  extension
sfd_c_src= glob.glob('mwdust/util/SFD_CodeC/*.c')

if not WIN32:
    sfd_libraries=['m']
else:
    sfd_libraries=[]
sfd_c= Extension('sfd_c',
                 sources=sfd_c_src,
                 libraries=sfd_libraries,
                 extra_compile_args=['-DLITTLE_ENDIAN'],
                 include_dirs=['mwdust/util/SFD_CodeC'])


#healpix  extension
healpix_c_src= glob.glob('mwdust/util/healpix_CodeC/*.c')

healpix_c= Extension('healpix_c',
                 sources=healpix_c_src,
                 libraries=sfd_libraries,
                 extra_compile_args=['-DLITTLE_ENDIAN'],
                 include_dirs=['mwdust/util/healpix_CodeC'])

ext_modules=[sfd_c, healpix_c]

install_requires= ['numpy','scipy','matplotlib','astropy','h5py','tqdm']
if not WIN32:
    install_requires.append('healpy')
setup(name='mwdust',
      version='1.3.dev0',
      description='Dust in the Milky Way',
      author='Jo Bovy',
      author_email='bovy@astro.utoronto.ca',
      license='New BSD',
      long_description=long_description,
      url='https://github.com/jobovy/mwdust',
      package_dir = {'mwdust/': ''},
      packages=['mwdust',
                'mwdust/util'],
      package_data={'mwdust/util':['extCurves/extinction.tbl',
                                   'extCurves/apj398709t6_ascii.txt']},
      install_requires=install_requires,
      ext_modules=ext_modules,
      classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python :: 3.6",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"]
      )
