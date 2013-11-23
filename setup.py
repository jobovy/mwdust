from setuptools import setup
from distutils.core import Extension
import sys
import subprocess
import glob

longDescription= ""

#SFD  extension
sfd_c_src= glob.glob('mwdust/util/SFD_CodeC/*.c')

sfd_libraries=['m']
sfd_c= Extension('sfd_c',
                 sources=sfd_c_src,
                 libraries=sfd_libraries,
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
      install_requires=['numpy','scipy','matplotlib'],
      ext_modules=ext_modules
      )
