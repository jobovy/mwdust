###############################################################################
#
#   DustMap3D: top-level class for a 3D dust map; all other dust maps inherit
#              from this
#
###############################################################################
import numpy
import os
import inspect
import urllib
import gzip
import tarfile
import shutil
from .util.tools import TqdmUpTo
try:
    from galpy.util import plot as bovy_plot
    _BOVY_PLOT_LOADED= True
except ImportError:
    _BOVY_PLOT_LOADED= False

dust_dir = os.environ.get("DUST_DIR")
if dust_dir is None:
    dust_dir = os.path.expanduser(os.path.join("~", ".mwdust"))
if not os.path.exists(dust_dir):
    os.mkdir(dust_dir)

class DustMap3D:
    """top-level class for a 3D dust map; all other dust maps inherit from this"""
    def __init__(self,filter=None):
        """
        NAME:
           __init__
        PURPOSE:
           Initialize the dust map
        INPUT:
           filter= filter to return the extinction in when called
        OUTPUT:
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        self._filter= filter
        self.download()  # download the map
        return None

    def __call__(self,*args,**kwargs):
        """
        NAME:
           __call__
        PURPOSE:
           evaluate the dust map
        INPUT:
           Either:
              (l,b,d) -  Galactic longitude, latitude (deg), and distance (kpc)
        OUTPUT:
        HISTORY:
           2013-11-24 - Started - Bovy (IAS)
        """
        if True: #(l,b,d)
            l,b,d= args
            if isinstance(d,(int,float,numpy.float32,numpy.float64)):
                d= numpy.array([d])
            try:
                return self._evaluate(l,b,d,**kwargs)
            except AttributeError:
                raise NotImplementedError("'_evaluate' for this DustMap3D not implemented yet")

    def plot(self,l,b,*args,**kwargs):
        """
        NAME:
           plot
        PURPOSE:
           plot the extinction along a given line of sight as a function of 
           distance
        INPUT:
           l,b - Galactic longitude and latitude (degree)
           range= distance range in kpc
           distmod= (False) if True, plot as a function of distance modulus (range is distmod range)
           bovy_plot.plot args and kwargs
        OUTPUT:
           plot to output device
        HISTORY:
           2013-12-11 - Written - Bovy (IAS)
        """
        if not _BOVY_PLOT_LOADED:
            raise NotImplementedError("galpy.util.bovy_plot could not be loaded, so there is no plotting; might have to install galpy (http://github.com/jobovy/galpy) for plotting")
        distmod= kwargs.pop('distmod',False)
        range= kwargs.pop('range',None)
        if range is None and distmod:
            range= [4.,19.]
        else:
            range= [0.,12.]
        nds= kwargs.get('nds',101)
        #First evaluate the dust map
        ds= numpy.linspace(range[0],range[1],nds)
        if distmod:
            adust= self(l,b,10.**(ds/5.-2.))
        else:
            adust= self(l,b,ds)
        #Add labels
        if distmod:
            kwargs['xlabel']= r'$\mathrm{Distance\ modulus}$'
        else:
            kwargs['xlabel']= r'$D\,(\mathrm{kpc})$'
        if not self._filter is None:
            kwargs['ylabel']= r'$A_{%s}\,(\mathrm{mag})$' % (self._filter.split(' ')[-1])
        else:
            kwargs['ylabel']= r'$E(B-V)\,(\mathrm{mag})$'
        return bovy_plot.plot(ds,adust,*args,**kwargs)

    
    @staticmethod
    def __downloader(url, fullfilename, name, test=False):
        if test:  # only for testing respond
            # import requests here to avoid including requests as a requirment in mwdust
            import requests
            r = requests.head(url, allow_redirects=True, verify=False)
            if r.status_code != 200:
                raise ConnectionError(f"Cannot find {name} data dile at {url}")
            r.close()
        else:
            with TqdmUpTo(unit="B", unit_scale=True, miniters=1, desc=name) as t:
                try:
                    opener=urllib.request.build_opener()
                    opener.addheaders=[('User-Agent','Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/36.0.1941.0 Safari/537.36')]
                    urllib.request.install_opener(opener)
                    urllib.request.urlretrieve(url, fullfilename, reporthook=t.update_to)
                    print(f"Downloaded {name} successfully to {fullfilename}")
                except urllib.error.HTTPError as emsg:
                    if "404" in str(emsg):
                        raise FileNotFoundError(f"{url} cannot be found on server, skipped")
                    else:
                        raise SystemError(f"Unknown error occurred - {emsg}")

    @classmethod
    def download(cls, test=False):
        """
        class method to download
        """
        if cls.__name__ == "SFD":
            sfd_ngp_path = os.path.join(dust_dir, "maps", "SFD_dust_4096_ngp.fits")
            if not os.path.exists(sfd_ngp_path):
                if not os.path.exists(os.path.join(dust_dir, "maps")):
                    os.mkdir(os.path.join(dust_dir, "maps"))
                _SFD_URL_NGP= "https://svn.sdss.org/public/data/sdss/catalogs/dust/trunk/maps/SFD_dust_4096_ngp.fits"
                cls.__downloader(_SFD_URL_NGP, sfd_ngp_path, "SFD_NGP", test=test)
            sfd_sgp_path = os.path.join(dust_dir, "maps", "SFD_dust_4096_sgp.fits")
            if not os.path.exists(sfd_ngp_path):
                _SFD_URL_SGP= "https://svn.sdss.org/public/data/sdss/catalogs/dust/trunk/maps/SFD_dust_4096_sgp.fits"
                cls.__downloader(_SFD_URL_SGP, sfd_sgp_path, "SFD_SGP", test=test)

        elif cls.__name__ == "Drimmel03":                
            drimmel_folder_path = os.path.abspath(os.path.join(inspect.getfile(cls), "..", "util", "drimmeldata"))
            drimmel_path = os.path.join(drimmel_folder_path, "data-for.tar.gz")
            if not os.path.exists(drimmel_path):
                if not os.path.exists(drimmel_folder_path):
                    os.mkdir(drimmel_folder_path)
                _DRIMMEL_URL= "https://zenodo.org/record/7340108/files/data-for.tar.gz"
                cls.__downloader(_DRIMMEL_URL, drimmel_path, "DRIMMEL03", test=test)
                if not test:
                    file = tarfile.open(drimmel_path)
                    file.extractall(drimmel_folder_path)
                    file.close()

        elif cls.__name__ == "Marshall06":
            marshall_folder_path = os.path.join(dust_dir, "marshall06")
            marshall_path = os.path.join(marshall_folder_path, "table1.dat.gz")
            marshall_readme_path = os.path.join(dust_dir, "marshall06", "ReadMe")
            if not os.path.exists(marshall_path[:-3]):
                if not os.path.exists(marshall_folder_path):
                    os.mkdir(marshall_folder_path)
                _MARSHALL_URL= "ftp://cdsarc.u-strasbg.fr/pub/cats/J/A%2BA/453/635/table1.dat.gz"
                cls.__downloader(_MARSHALL_URL, marshall_path, "MARSHALL06", test=test)
                if not test:
                    with open(marshall_path, "rb") as inf, open(os.path.join(marshall_folder_path, "table1.dat"), "w", encoding="utf8") as tof:
                        decom_str = gzip.decompress(inf.read()).decode("utf-8")
                        tof.write(decom_str)
            if not os.path.exists(marshall_readme_path):
                _MARSHALL_README_URL= "ftp://cdsarc.u-strasbg.fr/pub/cats/J/A%2BA/453/635/ReadMe"
                cls.__downloader(_MARSHALL_README_URL, marshall_readme_path, "MARSHALL06 README", test=test)

        elif cls.__name__ == "Sale14":
            sale_folder_path = os.path.join(dust_dir, "sale14")
            sale_path = os.path.join(sale_folder_path, "Amap.tar.gz")
            if not os.path.exists(sale_path[:-6] + "dat"):
                if not os.path.exists(sale_folder_path):
                    os.mkdir(sale_folder_path)
                _SALE_URL= "http://www.iphas.org/data/extinction/Amap.tar.gz"
                cls.__downloader(_SALE_URL, sale_path, "SALE14", test=test)
                if not test:
                    file = tarfile.open(sale_path)
                    file.extractall(sale_folder_path)
                    file.close()
                    # Fix one line in the dust map
                    with open(os.path.join(sale_folder_path, "tmp.dat"), "w") as fout:
                        with open(os.path.join(sale_folder_path, "Amap.dat"), "r") as fin:
                            for line in fin:
                                if "15960.40000" in line: # bad line
                                    newline= ''
                                    for ii,word in enumerate(line.split(' ')):
                                        if ii > 0: newline+= ' '
                                        if ii > 6 and len(word) > 9:
                                            word= "747.91400"
                                        newline+= word
                                    fout.write(newline+'\n')
                                else:
                                    fout.write(line)
                    shutil.move(os.path.join(sale_folder_path, "tmp.dat"), os.path.join(sale_folder_path, "Amap.dat"))

        elif cls.__name__ == "Green15":
            # Download Green et al. PanSTARRS data (alt.: http://dx.doi.org/10.7910/DVN/40C44C)
            green15_path = os.path.join(dust_dir, "green15", "dust-map-3d.h5")
            if not os.path.exists(green15_path):
                if not os.path.exists(os.path.join(dust_dir, "green15")):
                    os.mkdir(os.path.join(dust_dir, "green15"))
                _GREEN15_URL = "http://faun.rc.fas.harvard.edu/pan1/ggreen/argonaut/data/dust-map-3d.h5"
                cls.__downloader(_GREEN15_URL, green15_path, "GREEN15", test=test)

        elif cls.__name__ == "Green17":
            # Download Green et al. 2018 PanSTARRS data
            green17_path = os.path.join(dust_dir, "green17", "bayestar2017.h5")
            if not os.path.exists(green17_path):
                if not os.path.exists(os.path.join(dust_dir, "green17")):
                    os.mkdir(os.path.join(dust_dir, "green17"))
                _GREEN17_URL = "https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/LCYHJG/S7MP4P"
                cls.__downloader(_GREEN17_URL, green17_path, "GREEN17", test=test)

        elif cls.__name__ == "Green19":
            # Download Green et al. 2019 PanSTARRS data
            green19_path = os.path.join(dust_dir, "green19", "bayestar2019.h5")
            if not os.path.exists(green19_path):
                if not os.path.exists(os.path.join(dust_dir, "green19")):
                    os.mkdir(os.path.join(dust_dir, "green19"))
                _GREEN19_URL = "https://dataverse.harvard.edu/api/access/datafile/:persistentId?persistentId=doi:10.7910/DVN/2EJ9TX/1CUGA1"
                cls.__downloader(_GREEN19_URL, green19_path, "GREEN19", test=test)

        elif cls.__name__ == "Combined19":
            # Download the combined map: Marshall+Green19+Drimmel for full sky coverage
            combined19_path = os.path.join(dust_dir, "combined19", "combine19.h5")
            if not os.path.exists(combined19_path):
                if not os.path.exists(os.path.join(dust_dir, "combined19")):
                    os.mkdir(os.path.join(dust_dir, "combined19"))
                _COMBINED19_URL = "https://zenodo.org/record/3566060/files/combine19.h5"
                cls.__downloader(_COMBINED19_URL, combined19_path, "COMBINED19", test=test)

        elif cls.__name__ == "Combined15":
            # Download the combined map of Bovy et al. (2015): Marshall+Green+Drimmel for full sky coverage
            combined15_path = os.path.join(dust_dir, "combined15", "dust-map-3d.h5")
            if not os.path.exists(combined15_path):
                if not os.path.exists(os.path.join(dust_dir, "combined15")):
                    os.mkdir(os.path.join(dust_dir, "combined15"))
                _COMBINED15_URL = "https://zenodo.org/record/31262/files/dust-map-3d.h5"
                cls.__downloader(_COMBINED15_URL, combined15_path, "COMBINED15", test=test)

        else:
            raise NameError(f"Unknown class: {cls.__name__}")
