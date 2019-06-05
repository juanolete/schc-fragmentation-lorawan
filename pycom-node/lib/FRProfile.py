from FRConstants import *

class FRProfile:
    
    def __init__(self, window_size = 5, max_ack = 10, ret_timer = 10, 
                inact_timer = 10, mic_type = MIC32, mic_bsize = MIC32_bsize, 
                ruleid_bsize = 8, dtag_bsize = 8, w_bsize = 1, 
                fcn_bsize = 8):

        self._window_size = window_size
        self._max_ack_requests = max_ack
        self._retransmission_timer = ret_timer
        self._inactivity_timer = inact_timer
        self._mic_type = mic_type
        self._mic_size_bits = mic_bsize
        self._field_ruleid_size_bits = ruleid_bsize
        self._field_dtag_size_bits = dtag_bsize
        self._field_w_size_bits = w_bsize
        self._field_fcn_size_bits = fcn_bsize 
    
    
