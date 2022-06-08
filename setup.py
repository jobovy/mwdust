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

try:
    downloads_pos = sys.argv.index('--no-downloads')
except ValueError:
    try:
        all_downloads_pos = sys.argv.index('--all-downloads')
    except ValueError:
        _DOWNLOAD_SFD= True
        _DOWNLOAD_DRIMMEL= True
        _DOWNLOAD_MARSHALL= True
        _DOWNLOAD_SALE= False
        _DOWNLOAD_GREEN= False
        _DOWNLOAD_GREEN17= False
        _DOWNLOAD_GREEN19= True
        _DOWNLOAD_COMBINED= True
        _DOWNLOAD_COMBINED19= True
    else:
        del sys.argv[all_downloads_pos]
        _DOWNLOAD_SFD= True
        _DOWNLOAD_DRIMMEL= True
        _DOWNLOAD_MARSHALL= True
        _DOWNLOAD_SALE= True
        _DOWNLOAD_GREEN= True
        _DOWNLOAD_GREEN17= True
        _DOWNLOAD_GREEN19= True
        _DOWNLOAD_COMBINED= True
        _DOWNLOAD_COMBINED19= True
else:
    del sys.argv[downloads_pos]
    _DOWNLOAD_SFD= False
    _DOWNLOAD_DRIMMEL= False
    _DOWNLOAD_MARSHALL= False
    _DOWNLOAD_SALE= False
    _DOWNLOAD_GREEN= False
    _DOWNLOAD_GREEN17= False
    _DOWNLOAD_GREEN19= False
    _DOWNLOAD_COMBINED= False
    _DOWNLOAD_COMBINED19= False
    
try:
    test_downloads_pos= sys.argv.index('--test-downloads')
except ValueError:
    _TEST_DOWNLOADS= False
else:
    del sys.argv[test_downloads_pos]
    _TEST_DOWNLOADS= True    

try:
    verbose_downloads_pos= sys.argv.index('--verbose-downloads')
except ValueError:
    _VERBOSE_DOWNLOADS= False
else:
    del sys.argv[test_downloads_pos]
    _VERBOSE_DOWNLOADS= True    

def download_file(url,output,desc,notest=False):
    print('\033[1m'+'Downloading {} dust maps ...'.format(desc)+'\033[0m')
    try:
        cmd= ['curl','-fL',url]
        if not _VERBOSE_DOWNLOADS:
            cmd.append('--silent')
        if _TEST_DOWNLOADS:
            if notest: return None
            cmd.extend(['--output','-','--head'])
        else:
            cmd.extend(['-o',output])
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        print('\033[1m'+"Downloading {} dust-map data from {} failed ...".format(desc,url)+'\033[0m')
        if _TEST_DOWNLOADS:
            raise
    return None
        
def chown_file(output):
    if not _TEST_DOWNLOADS:
        try:
            subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                   output])
        except (subprocess.CalledProcessError,TypeError):
            print('\033[1m'+"Problem changing ownership of data file..."+'\033[0m')
    return None

#Download SFD maps
_SFD_URL_NGP= 'https://svn.sdss.org/public/data/sdss/catalogs/dust/trunk/maps/SFD_dust_4096_ngp.fits'
_SFD_URL_SGP= 'https://svn.sdss.org/public/data/sdss/catalogs/dust/trunk/maps/SFD_dust_4096_sgp.fits'
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
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
            download_file(_SFD_URL_NGP,
                          os.path.join(os.getenv('DUST_DIR'),'maps',
                                       'SFD_dust_4096_ngp.fits'),
                          'SFD')
            chown_file(os.path.join(os.getenv('DUST_DIR'),
                       'maps','SFD_dust_4096_ngp.fits'))

        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'maps',
                                           'SFD_dust_4096_sgp.fits')):
            download_file(_SFD_URL_SGP,
                          os.path.join(os.getenv('DUST_DIR'),'maps',
                                       'SFD_dust_4096_sgp.fits'),
                          'SFD')
            chown_file(os.path.join(os.getenv('DUST_DIR'),
                       'maps','SFD_dust_4096_sgp.fits'))

#Download Drimmel data
_DRIMMEL_URL= 'ftp://ftp.oato.inaf.it/astrometria/extinction/data-for.tar.gz'
if _DOWNLOAD_DRIMMEL \
        and sys.argv[1] in ('build','install','develop','bdist','bdist_egg'):
    if not os.path.exists('mwdust/util/drimmeldata/data-for.tar.gz'):
        download_file(_DRIMMEL_URL,
                      'mwdust/util/drimmeldata/data-for.tar.gz',
                      'Drimmel et al. (2003)')
        if not _TEST_DOWNLOADS:
            try:
                subprocess.check_call(['tar','xvzf',
                                    'mwdust/util/drimmeldata/data-for.tar.gz',
                                    '-C','mwdust/util/drimmeldata/'])
            except subprocess.CalledProcessError:
                print("Untarring Drimmel dust-map data failed ...")

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
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'marshall06',
                                                'table1.dat')):
            download_file('{}/table1.dat.gz'.format(_MARSHALL_URL),
                          os.path.join(os.getenv('DUST_DIR'),
                                       'marshall06','table1.dat.gz'),
                          'Marshall et al. (2006)')     
            if not _TEST_DOWNLOADS:
                try:
                    subprocess.check_call(['gzip','-d',
                                        os.path.join(os.getenv('DUST_DIR'),
                                                        'marshall06',
                                                        'table1.dat.gz')],
                                        shell=WIN32)
                except (subprocess.CalledProcessError,FileNotFoundError):
                    print('\033[1m'+"Gunzipping Marshall et al. dust-map data failed ..."+'\033[0m')
            chown_file(os.path.join(os.getenv('DUST_DIR'),'marshall06',
                       'table1.dat'))
            #Also download the ReadMe file
            download_file('{}/ReadMe'.format(_MARSHALL_URL),
                          os.path.join(os.getenv('DUST_DIR'),
                                       'marshall06','ReadMe'),
                          'Marshall et al. (2006)')
            chown_file(os.path.join(os.getenv('DUST_DIR'),'marshall06',
                                    'ReadMe'))

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
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
        if not (os.path.exists(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                                'table1.dat')) 
                or os.path.exists(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                                'Amap.dat'))):
            if _SALE_CDS:
                download_file('{}/table1.dat.gz'.format(_SALE_URL),
                              os.path.join(os.getenv('DUST_DIR'),
                                           'sale14',
                                           'table1.dat.gz'),
                              'Sale')
                if not _TEST_DOWNLOADS:
                    try:
                        subprocess.check_call(['gzip','-d',
                                               os.path.join(os.getenv('DUST_DIR'),
                                                            'sale14',
                                                            'table1.dat.gz')])
                    except subprocess.CalledProcessError:
                        print('\033[1m'+"Gunzipping Sale et al. dust-map data failed ..."+'\033[0m')
                    chown_file(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                            'table1.dat'))
                #Also download the ReadMe file
                download_file('{}/ReadMe'.format(_SALE_URL),
                              os.path.join(os.getenv('DUST_DIR'),
                                           'sale14',
                                           'ReadMe'),
                              'Sale')
                chown_file(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                        'ReadMe'))
            else:
                download_file(_SALE_URL,
                              os.path.join(os.getenv('DUST_DIR'),
                                                        'sale14',
                                                        'Amap.tar.gz'),
                              'Sale')
                if not _TEST_DOWNLOADS:
                    try:
                        subprocess.check_call(['tar','xvzf',
                                            os.path.join(os.getenv('DUST_DIR'),
                                                            'sale14',
                                                            'Amap.tar.gz'),
                                            '-C',
                                            os.path.join(os.getenv('DUST_DIR'),
                                                            'sale14')])
                    except subprocess.CalledProcessError:
                        print('\033[1m'+"Untarring/unzipping Sale et al. dust-map data failed ..."+'\033[0m')
                    try:
                        os.remove(os.path.join(os.getenv('DUST_DIR'),'sale14',
                                            'Amap.tar.gz'))
                    except subprocess.CalledProcessError:
                        print('\033[1m'+"Removing Sale et al. dust-map tarred data failed ..."+'\033[0m')
            # Fix one line in the dust map
            if not _TEST_DOWNLOADS:
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
                shutil.move('tmp.dat',os.path.join(os.getenv('DUST_DIR'),'sale14',
                                                'Amap.dat'))

#Download Green et al. PanSTARRS data (alt.: http://dx.doi.org/10.7910/DVN/40C44C)
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
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'green15',
                                           'dust-map-3d.h5')):
            download_file(_GREEN_URL,
                          os.path.join(os.getenv('DUST_DIR'),
                                       'green15',
                                       'dust-map-3d.h5'),
                          'Green et al. (2015)')
            chown_file(os.path.join(os.getenv('DUST_DIR'),'green15',
                                    'dust-map-3d.h5'))

#Download Green et al. 2018 PanSTARRS data
_GREEN_URL= 'https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/LCYHJG/S7MP4P'
if _DOWNLOAD_GREEN17 and sys.argv[1] in ('install','develop'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'green17')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'green17'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'green17')])
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'green17',
                                           'bayestar2017.h5')):
            download_file(_GREEN_URL,
                          os.path.join(os.getenv('DUST_DIR'),
                                       'green17',
                                       'bayestar2017.h5'),
                          'Green et al. (2018)',
                          notest=True)
            chown_file(os.path.join(os.getenv('DUST_DIR'),'green17',
                                    'bayestar2017.h5'))

#Download Green et al. 2019 PanSTARRS data
_GREEN_URL= 'https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/2EJ9TX/1CUGA1'
if _DOWNLOAD_GREEN19 and sys.argv[1] in ('install','develop'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'green19')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'green19'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'green19')])
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'green19',
                                           'bayestar2019.h5')):
            download_file(_GREEN_URL,
                          os.path.join(os.getenv('DUST_DIR'),
                                       'green19',
                                       'bayestar2019.h5'),
                          'Green et al. (2019)',
                          notest=True)
            chown_file(os.path.join(os.getenv('DUST_DIR'),'green19',
                       'bayestar2019.h5'))

#Download the combined map: Marshall+Green19+Drimmel for full sky coverage
_COMBINED_URL= 'https://zenodo.org/record/3566060/files/combine19.h5'
if _DOWNLOAD_COMBINED19 and sys.argv[1] in ('install','develop'):
    if os.getenv('DUST_DIR') is None:
        raise IOError('Please define an environment variable DUST_DIR as a top-level directory for various dust maps\nIf using sudo, you may have to run sudo -E to propagate environment variables')
    else:
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),
                                           'combined19')):
            os.mkdir(os.path.join(os.getenv('DUST_DIR'),'combined19'))
            try:
                subprocess.check_call(['chown',os.getenv('SUDO_USER'),
                                       os.path.join(os.getenv('DUST_DIR'),
                                                    'combined19')])
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'combined19',
                                           'combine19.h5')):
            download_file(_COMBINED_URL,
                          os.path.join(os.getenv('DUST_DIR'),
                                       'combined19',
                                       'combine19.h5'),
                          'combined 2019')
            chown_file(os.path.join(os.getenv('DUST_DIR'),'combined19',
                                    'combine19.h5'))

#Download the combined map of Bovy et al. (2015): Marshall+Green+Drimmel for full sky coverage
_COMBINED_URL= 'https://zenodo.org/record/31262/files/dust-map-3d.h5'
if _DOWNLOAD_COMBINED and sys.argv[1] in ('install','develop'):
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
            except (subprocess.CalledProcessError,TypeError):
                print('\033[1m'+"Problem changing ownership of data directory ..."+'\033[0m')
        if not os.path.exists(os.path.join(os.getenv('DUST_DIR'),'combined15',
                                           'dust-map-3d.h5')):
            download_file(_COMBINED_URL,
                          os.path.join(os.getenv('DUST_DIR'),
                                       'combined15',
                                       'dust-map-3d.h5'),
                          'combined 2015')
            chown_file(os.path.join(os.getenv('DUST_DIR'),
                                    'combined15',
                                    'dust-map-3d.h5'))

if _TEST_DOWNLOADS:
    sys.exit()

#SFD  extension
sfd_c_src= glob.glob('mwdust/util/SFD_CodeC/*.c')

sfd_libraries=['m']
sfd_c= Extension('sfd_c',
                 sources=sfd_c_src,
                 libraries=sfd_libraries,
                 extra_compile_args=['-DLITTLE_ENDIAN'],
                 include_dirs=['mwdust/util/SFD_CodeC'])

if not WIN32:
    ext_modules=[sfd_c]
else:
    ext_modules= None

setup(name='mwdust',
      version='1.2.dev',
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
                                   'extCurves/apj398709t6_ascii.txt',
                                   'drimmeldata/*.dat']},
      install_requires=['numpy','scipy','matplotlib','asciitable',
                        'h5py'],#,'healpy'],
      ext_modules=ext_modules,
      classifiers=[
        "Development Status :: 6 - Mature",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: C",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Topic :: Scientific/Engineering :: Astronomy",
        "Topic :: Scientific/Engineering :: Physics"]
      )
