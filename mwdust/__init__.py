from mwdust.SFD import SFD
from mwdust.Marshall06 import Marshall06
from mwdust.Drimmel03 import Drimmel03
from mwdust.Sale14 import Sale14
from mwdust.Green15 import Green15
from mwdust.Green17 import Green17
from mwdust.Green19 import Green19
from mwdust.Combined15 import Combined15
from mwdust.Combined19 import Combined19
from mwdust.Zero import Zero

__version__ = "1.4"


def download_all(test=False):
    SFD.download(test=test)
    Marshall06.download(test=test)
    Drimmel03.download(test=test)
    Sale14.download(test=test)
    Green15.download(test=test)
    Green17.download(test=test)
    Green19.download(test=test)
    Combined15.download(test=test)
    Combined19.download(test=test)
