from FRCommon import FRModes as Modes


class FRProfile:

    def __init__(self, rule_id_size=3, l2_word_size=8, dtag_size=1, w_size=1, fcn_size=3):
        self.rule_id_size = rule_id_size
        self.l2_word_size = l2_word_size

        # for fragmentation:
        self.fragmentation = False

        self.mode = None

        self.dtag_size = dtag_size

        self.w_size = w_size
        self.use_windows = None
        self.WINDOW_SIZE = None

        self.fcn_size = fcn_size

        self.mic_size = 32
        self.mic_algo = 'CRC32'

        self.retransmission_timer = None  # Not used
        self.inactivity_timer = None

        self.MAX_ACK_REQUESTS = None

        self.penultimate_tile_smaller = False  # For ACK-on-Error mode

        return

    def select_fragmentation_mode(self, mode: Modes, inactivity_timer=12*3600, max_ack_requests=10,
                                  window_size=7, penultimate_tile_smaller=False):
        self.mode = mode
        self.WINDOW_SIZE = window_size
        self.inactivity_timer = inactivity_timer
        self.MAX_ACK_REQUESTS = max_ack_requests
        if mode == Modes.NO_ACK:
            self.use_windows = False
            self.penultimate_tile_smaller = False

        if mode == Modes.ALWAYS_ACK:
            self.use_windows = True
            self.penultimate_tile_smaller = False

        if mode == Modes.ACK_ON_ERROR:
            self.use_windows = True
            self.penultimate_tile_smaller = penultimate_tile_smaller

        return

    def enable_fragmentation(self):
        self.fragmentation = True
        return

    def disable_fragmentation(self):
        self.fragmentation = False
        return
