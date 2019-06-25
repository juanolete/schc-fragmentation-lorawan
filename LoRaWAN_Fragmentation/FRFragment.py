from bitstring import Bits
from FRCommon import *


class FRFragmentEngine:

    def __init__(self, profile, rule_id, dtag):
        self.l2_word_size = profile.l2_word_size
        self.rule_id_size = profile.rule_id_size
        self.dtag_size = profile.dtag_size
        self.w_size = profile.w_size
        self.fcn_size = profile.fcn_size
        self.mic_size = profile.mic_size
        self.WINDOW_SIZE = profile.WINDOW_SIZE
        self.use_windows = profile.use_windows
        self.rule_id = rule_id
        self.dtag = dtag
        return

    # Create Regular Fragment message
    def create_regular_fragment(self, tile, window=0, fcn_number=0):

        rid = Bits(uint=self.rule_id, length=self.rule_id_size)
        dtag = Bits(0)
        if self.dtag_size > 0:
            dtag = Bits(uint=self.dtag, length=self.dtag_size)
        w = Bits(0)
        if self.use_windows:
            w = Bits(uint=(window & lsb_mask[self.w_size]), length=self.w_size)
        fcn = Bits(uint=fcn_number, length=self.fcn_size)

        header = rid + dtag + w + fcn
        payload = tile.get_bits()
        fragment = header + payload
        # print(fragment)
        return fragment

    # Create SCHC All-1 fragment message
    def create_all_1_fragment(self, tile, mic_value, window=0):

        rid = Bits(uint=self.rule_id, length=self.rule_id_size)
        dtag = Bits(0)
        if self.dtag_size > 0:
            dtag = Bits(uint=self.dtag, length=self.dtag_size)
        w = Bits(0)
        w_size = 0
        if self.use_windows:
            w = Bits(uint=(window & lsb_mask[self.w_size]), length=self.w_size)
            w_size = self.w_size
        fcn = Bits(uint=lsb_mask[self.fcn_size], length=self.fcn_size)
        mic = Bits(uint=mic_value, length=self.mic_size)

        header = rid + dtag + w + fcn + mic
        payload = tile.get_bits()
        padding = Bits(0)
        pad_bits = self.last_tile_padding(tile)
        if pad_bits > 0:
            padding = Bits(uint=0, length=pad_bits)
        fragment = header + payload + padding
        return fragment

    # Create SCHC ACK
    def create_ack(self, window=0, bitmap=0):
        rid = Bits(uint=self.rule_id, length=self.rule_id_size)
        dtag = Bits(0)
        if self.dtag_size > 0:
            dtag = Bits(uint=self.dtag, length=self.dtag_size)
        header_size = self.rule_id_size + self.dtag_size + 1
        if self.use_windows:
            w = Bits(uint=window & lsb_mask[self.w_size], length=self.w_size)
            header_size += self.w_size
            # Calculate C bit and Compressed Bitmap
            compressed_bitmap = None
            compressed_bitmap_size = None
            if bitmap != lsb_mask[self.WINDOW_SIZE]:  # Si Bitmap != 0b111...1
                c = Bits(uint=0, length=1)

                # ####Falta calcular compressed Bitmap y size ####
                header_size += compressed_bitmap_size
                comp_bmp = Bits(uint=compressed_bitmap, length=compressed_bitmap_size)

                # Padding calculation
                padding = Bits(0)
                pad_bits = padding_bits(header_size, self.l2_word_size)
                if pad_bits > 0:
                    padding = Bits(uint=0, length=pad_bits)

                fragment = rid + dtag + w + c + comp_bmp + padding
                return fragment

            else:
                c = Bits(uint=1, length=1)

                # Padding calculation
                padding = None
                pad_bits = padding_bits(header_size, self.l2_word_size)
                if pad_bits > 0:
                    padding = Bits(uint=0, length=pad_bits)

                fragment = rid + dtag + w + c + padding
                return fragment

        else:
            print("This mode dont use SCHC ACK messages")
            return

    # Create SCHC ACK REQ
    def create_ack_req(self, window):
        rid = Bits(uint=self.rule_id, length=self.rule_id_size)
        dtag = Bits(0)
        if self.dtag_size > 0:
            dtag = Bits(uint=self.dtag, length=self.dtag_size)
        w = Bits(0)
        w_size = 0
        if self.use_windows:
            w = Bits(uint=(window & lsb_mask[self.w_size]), length=self.w_size)
            w_size = self.w_size
        fcn = Bits(uint=0, length=self.fcn_size)

        header_size = self.rule_id + self.dtag_size + w_size + self.fcn_size

        # Padding calculation
        padding = Bits(0)
        pad_bits = padding_bits(header_size, self.l2_word_size)
        if pad_bits > 0:
            padding = Bits(uint=0, length=pad_bits)

        fragment = rid + dtag + w + fcn + padding
        return fragment

    # Create SCHC Sender-Abort
    def create_sender_abort(self):
        rid = Bits(uint=self.rule_id, length=self.rule_id_size)
        dtag = Bits(0)
        if self.dtag_size > 0:
            dtag = Bits(uint=self.dtag, length=self.dtag_size)
        w = Bits(0)
        w_size = 0
        if self.use_windows:
            w = Bits(uint=lsb_mask[self.w_size], length=self.w_size)
            w_size = self.w_size
        fcn = Bits(uint=lsb_mask[self.fcn_size], length=self.fcn_size)

        header_size = self.rule_id_size + self.dtag_size + w_size + self.fcn_size

        # Padding Calculation
        padding = Bits(0)
        pad_bits = padding_bits(header_size, self.l2_word_size)
        if pad_bits > 0:
            padding = Bits(uint=0, length=pad_bits)

        fragment = rid + dtag + w + fcn + padding
        return fragment

    def create_receiver_abort(self):
        rid = Bits(uint=self.rule_id, length=self.rule_id_size)
        dtag = Bits(0)
        if self.dtag_size > 0:
            dtag = Bits(uint=self.dtag, length=self.dtag_size)
        w = Bits(0)
        w_size = 0
        if self.use_windows:
            w = Bits(uint=lsb_mask[self.w_size], length=self.w_size)
            w_size = self.w_size
        c = Bits(uint=1, length=1)
        header_size = self.rule_id_size + self.dtag_size + w_size + 1

        # Padding Calculation
        padding = Bits(0)
        pad_bits = padding_bits(header_size, self.l2_word_size)
        if pad_bits > 0:
            padding = Bits(uint=lsb_mask[pad_bits], length=pad_bits)
        else:
            padding = Bits(uint=lsb_mask[8], length=8)

        fragment = rid + dtag + w + c + padding
        return fragment

    # Calculate padding bits for All-1 message and MIC calculation
    def last_tile_padding(self, last_tile):
        w_size = 0
        if self.use_windows:
            w_size = self.w_size

        fragment_size = self.rule_id_size + self.dtag_size + w_size \
            + self.fcn_size + self.mic_size + last_tile.fullBits

        pad_bits = padding_bits(fragment_size, self.l2_word_size)
        return pad_bits

    def regular_fragment_header_size(self):
        w_size = 0
        if self.use_windows:
            w_size = self.w_size

        return self.rule_id_size + self.dtag_size + w_size + self.fcn_size
