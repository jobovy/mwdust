mwdust
======

**Dust in 3D in the Milky Way**

.. image:: https://github.com/jobovy/mwdust/workflows/build/badge.svg
   :target: https://github.com/jobovy/mwdust/actions?query=workflow%3Abuild

.. image:: http://img.shields.io/pypi/v/mwdust.svg
   :target: https://pypi.python.org/pypi/mwdust/

.. image:: http://img.shields.io/badge/license-New%20BSD-brightgreen.svg
   :target: https://github.com/jobovy/mwdust/blob/main/LICENSE

Installation
-------------

Please define an environment variable ``DUST_DIR`` before installing
the code; this is a directory that will contain the dust data.

Standard python setup.py build/install

Either

``sudo python setup.py install``

or 

``python setup.py install --prefix=/some/directory/``

The installation automatically downloads the relevant dust data. You
might have to define an environment variable ``SUDO_USER`` if not
installing with sudo and you might have to use the ``-E`` option when
you are installing with sudo to transfer your environment variables to
sudo.

Note that this code currently does not really work on Windows. The 
installation command should download and otherwise work as long as 
you have the ``gzip`` utility (e.g., through install ``7zip``), 
but the SFD code will not be compiled (so the ``SFD`` map will not 
be available) and because ``healpy`` is unavailable on Windows, all 
HEALPIx-based maps (e.g., `CombinedXX`, `GreenXX`) will also not 
work. Thus, the code is only marginally useful on Windows. Install 
on Linux/Mac OS for full features.

Dust Data
---------

The code can automatically download all of the necessary data. By
default, only the most commonly-used dust maps are downloaded; to
download all maps, use the ``--all-downloads`` installation option
(you can just re-run the installation with this option to add this
later).  The installation option ``--no-downloads`` turns all
downloads off. By default, downloads are run without showing any 
progress, but if you want to see the downloads's progression, use 
``--verbose-downloads``.

The data are put in subdirectories of a directory ``DUST_DIR``, with
roughly the following lay-out::

    $DUST_DIR/
       combined15/
          dust-map-3d.h5
       combined19/
          combine19.h5
       green15/
          dust-map-3d.h5
       green17/
          bayestar2017.h5
       green19/
          bayestar2019.h5
       maps/
          SFD_dust_4096_ngp.fits
	  SFD_dust_4096_sgp.fits
       marshall06/
          ReadMe
	  table1.dat
       sale14/
          Amap.dat
          ReadMe

The data for the Drimmel et al. (2003) map is installed in the code
directory, because it is not very large.

Usage
------

All of the maps can be initialized similar to::

    import mwdust
    drimmel= mwdust.Drimmel03(filter='2MASS H')
    combined= mwdust.Combined15(filter='2MASS H')
    combined19= mwdust.Combined19(filter='2MASS H')
    sfd= mwdust.SFD(filter='2MASS H')

which sets up the Drimmel et al. (2003) map, the combined Bovy et
al. (2016) map, an updated version of the combined map using the Green
et al. (2019) Bayestar19 map, and the SFD map for the *H*-band
filter. The maps can be evaluate for a given Galactic longitude *l*,
Galactic latitude *b*, and an array (or scalar) of distances *D*::

	 drimmel(60.,0.,3.) # inputs are (l,b,D)
	 array([ 0.38813341])
	 combined(30.,3.,numpy.array([1.,2.,3.,10.]))
	 array([ 0.22304147,  0.55687252,  0.86694602,  1.18779507])
	 # SFD is just the constant SFD extinction
	 sfd(30.,3.,numpy.array([1.,2.,3.]))
	 array([ 1.19977335,  1.19977335,  1.19977335])

and they can be plotted as a function of distance at a given (l,b)::

    combined.plot(55.,0.5) # inputs are (l,b)

(plot not shown). Maps that are derived from the
``HierarchicalHealpixMap.py`` class (currently all Green-type maps and
the combined maps) can also be plotted on the sky using a Mollweide
projection at a given distance using::

    combined.plot_mollweide(5.) # input is distance in kpc

Supported bandpasses
---------------------

Currently only a few filters are supported; if no filter is supplied,
*E(B-V)* is returned on the SFD scale if the object is initialized
with ``sf10=True`` (which tells the code to use re-scalings from
`Schlafly & Finkbeiner 2011
<http://adsabs.harvard.edu/abs/2011ApJ...737..103S>`__). ``sf10=True``
is the default initialization for every map, so be careful in
interpreting the raw *E(B-V)* that come out of the code. *Only use*
``sf10=False`` *when you have an extinction map in true E(B-V)*, **not**
*SFD E(B-V)*. No map currently included in this package is in this
situation, so using ``sf10=False`` is never recommended.

To check what bandpasses are supported on the ``sf10=True`` scale do
(these are all the bandpasses from Table 6 in `Schlafly & Finkbeiner
2011 <http://adsabs.harvard.edu/abs/2011ApJ...737..103S>`__)::

   from mwdust.util import extCurves  
   extCurves.avebvsf.keys()

which gives::

      ['Stromgren u',
       'Stromgren v',
       'ACS clear',
       'CTIO R',
       'CTIO V',
       'CTIO U',
       'CTIO I',
       ...]

To check the bandpasses that are supported on the old SFD scale (``sf10=False``), do::

   numpy.array(extCurves.avebv.keys())[True-numpy.isnan(extCurves.avebv.values())]

which gives::

      array(['CTIO R', 'CTIO V', 'CTIO U', 'CTIO I', 'CTIO B', 'DSS-II i',
       'DSS-II g', 'WISE-1', 'WISE-2', 'DSS-II r', 'UKIRT H', 'UKIRT J',
       'UKIRT K', 'IRAC-1', 'IRAC-2', 'IRAC-3', 'IRAC-4', '2MASS H',
       'SDSS r', 'SDSS u', 'SDSS z', 'SDSS g', 'SDSS i', '2MASS Ks',
       '2MASS J'], 
      dtype='|S14'

Acknowledgements
-----------------

When making use of this code in a publication, please cite `Bovy et
al. (2015a) <http://arxiv.org/abs/1509.06751>`__. Also cite the relevant papers for the dust
map that you use:

* **mwdust.SFD**: `Schlegel et al. (1998) <http://adsabs.harvard.edu/abs/1998ApJ...500..525S>`__

* **mwdust.Drimmel03**: `Drimmel et al. (2003) <http://adsabs.harvard.edu/abs/2003A%26A...409..205D>`__

* **mwdust.Marshall06**: `Marshall et al. (2006) <http://adsabs.harvard.edu/abs/2006A%26A...453..635M>`__

* **mwdust.Sale14**: `Sale et al. (2014) <http://adsabs.harvard.edu/abs/2014MNRAS.443.2907S>`__

* **mwdust.Green15**: `Green et al. (2015) <https://ui.adsabs.harvard.edu/abs/2015ApJ...810...25G>`__

* **mwdust.Green17**: `Green et al. (2018) <https://ui.adsabs.harvard.edu/abs/2018MNRAS.478..651G>`__ (added by `@jan-rybizki <https://github.com/jan-rybizki>`__)

* **mwdust.Green19**: `Green et al. (2019) <https://ui.adsabs.harvard.edu/abs/2019arXiv190502734G>`__ (added by `@jan-rybizki <https://github.com/jan-rybizki>`__)

* **mwdust.Combined15**: Combination of `Marshall et al. (2006) <http://adsabs.harvard.edu/abs/2006A%26A...453..635M>`__ (**mwdust.Marshall06**), `Green et al. (2015) <http://adsabs.harvard.edu/abs/2015arXiv150701005G>`__ (**mwdust.Green15**), and `Drimmel et al. (2003) <http://adsabs.harvard.edu/abs/2003A%26A...409..205D>`__ (**mwdust.Green15**); see `Bovy et al. (2015a) <http://adsabs.harvard.edu/abs/2015arXiv150906751B>`__

* **mwdust.Combined19**: Similar to **mwdust.Combined15**, but using **mwdust.Green19** instead of **mwdust.Green15**; see `Bovy et al. (2015a) <http://adsabs.harvard.edu/abs/2015arXiv150906751B>`__ for details on the combination (added by `@jan-rybizki <https://github.com/jan-rybizki>`__)

* **mwdust.Zero**: `Bovy et al. (2015b) <http://adsabs.harvard.edu/abs/2015arXiv150905796B>`__ :smirk:
