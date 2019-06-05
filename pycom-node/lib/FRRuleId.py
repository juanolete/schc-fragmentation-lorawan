from FRConstants import *

class FRRuleID:

    def __init__(self, id_number, profile, fragmentation = True, frag_mode = ALWAYS_ACK):
        self._id = id_number
        self._profile = profile
        self._frag_on = fragmentation
        self._frag_mode = frag_mode
    

