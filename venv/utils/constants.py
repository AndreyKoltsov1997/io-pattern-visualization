#!/usr/bin/env python3

import sys, os
from utils.constants import *

sys.path.append(os.pardir)
sys.path.append(".")

class IOSNOOP_PARSING:
    TIME_VALUE_INDEX = 0
    PID_VALUE_INDEX = 2
    BYTES_VALUE_INDEX = 6
    LATENCY_VALUE_INDEX = 7

