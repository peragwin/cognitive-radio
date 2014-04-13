from __future__ import division

import numpy as np
import scipy.signal as sp

from FSK import *
from QAM import *
from paudio import *
from syncronization import *

def realtimeDecoder(f0, f1, n, symbol_length, sync_pulse = None):
    
    if not sync_pulse:
        sync_pulse = genSyncPulse()

    
    rec_signal = bufferedRecord()
