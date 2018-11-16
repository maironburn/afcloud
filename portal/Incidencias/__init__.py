
from portal.Utils.logger import *
import os,sys
from afcloud.settings import MEDIA_ROOT



logger=getLogger()

if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)
    