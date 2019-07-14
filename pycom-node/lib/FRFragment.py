from bitstring import Bits
from FRBitmap import FRBitmap as Bitmap
from FRTile import FRTile as Tile
from FRCommon import *
from FRCommon import FRMessages as Messages


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
    def create_regular_fragment(self, tile: Tile, window=0, fcn_number=0):

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
    def create_all_1_fragment(self, tile: Tile, mic_value, window=0):

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
    def create_ack(self, bitmap: Bitmap, window=0):
        rid = Bits(uint=self.rule_id, length=self.rule_id_size)
        dtag = Bits(0)
        if self.dtag_size > 0:
            dtag = Bits(uint=self.dtag, length=self.dtag_size)
        header_size = self.rule_id_size + self.dtag_size + 1
        if self.use_windows:
            w = Bits(uint=window & lsb_mask[self.w_size], length=self.w_size)
            header_size += self.w_size
            # Calculate C bit and Compressed Bitmap
            if bitmap.get_value() != lsb_mask[self.WINDOW_SIZE]:  # Si Bitmap != 0b111...1
                c = Bits(uint=0, length=1)
                padding = Bits(0)
                pad_bits = padding_bits(header_size, self.l2_word_size)
                if pad_bits > bitmap.size:
                    comp_bmp = Bits(uint=bitmap.get_value(), length=bitmap.size)
                    padding = Bits(uint=0, length=pad_bits-bitmap.size)
                elif pad_bits == bitmap.size:
                    comp_bmp = Bits(uint=bitmap.get_value(), length=bitmap.size)
                else:
                    msb_to_take = bitmap.get_msb_to_take()
                    if msb_to_take <= pad_bits:
                        comp_bmp = Bits(uint=bitmap.get_value_msb(pad_bits), length=pad_bits)
                    else:
                        comp_bmp = Bits(uint=bitmap.get_value(), length=bitmap.size)
                        pad_bits = padding_bits(header_size+bitmap.size, self.l2_word_size)
                        padding = Bits(uint=0, length=pad_bits)
                fragment = rid + dtag + w + c + comp_bmp + padding
                return fragment

            else:
                c = Bits(uint=1, length=1)

                # Padding calculation
                padding = Bits(0)
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

        header_size = self.rule_id_size + self.dtag_size + w_size + self.fcn_size

        # Padding Calculation
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

    def sender_message_recovery(self, fragment: bytes):
        fragment_bits_left = len(fragment) * 8
        octet_bits_left = 8
        octet_index = 0

        # headers declaration
        rid = None
        dtag = None
        w = None
        c = None
        comp_bmp = None

        # Take Rule ID
        rid, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.rule_id_size,
                                                                                         fragment,
                                                                                         fragment_bits_left,
                                                                                         octet_index,
                                                                                         octet_bits_left)
        # Take DTag
        if self.dtag_size > 0:
            dtag, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.dtag_size,
                                                                                              fragment,
                                                                                              fragment_bits_left,
                                                                                              octet_index,
                                                                                              octet_bits_left)
        # Take W
        if self.use_windows > 0:
            w, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.w_size,
                                                                                           fragment,
                                                                                           fragment_bits_left,
                                                                                           octet_index,
                                                                                           octet_bits_left)
        # Take C
        c, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(1,
                                                                                       fragment,
                                                                                       fragment_bits_left,
                                                                                       octet_index, octet_bits_left)
        # Take compressed bitmap and message type
        message_type = None
        if c.get_bits().int:  # Si c=1
            if fragment_bits_left == 0:
                message_type = Messages.ACK
            else:
                aux_byte = fragment[octet_index] & lsb_mask[octet_bits_left]
                if aux_byte == 0:
                    message_type = Messages.ACK
                else:
                    message_type = Messages.RECEIVER_ABORT
        else:  # Si c=0
            message_type = Messages.ACK
            # Buscar compressed bitmap
            if fragment_bits_left <= self.WINDOW_SIZE:
                comp_bmp, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(
                    fragment_bits_left, fragment, fragment_bits_left, octet_index, octet_bits_left)
            else:
                comp_bmp, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(
                    self.WINDOW_SIZE, fragment, fragment_bits_left, octet_index, octet_bits_left)

        headers = [rid, dtag, w, c, comp_bmp]
        return message_type, headers

    def receiver_message_recovery(self, fragment: bytes):
        fragment_bits_left = len(fragment) * 8
        octet_bits_left = 8
        octet_index = 0

        # Headers declaration
        rid = None
        dtag = None
        w = None
        fcn = None
        mic = None
        payload = None

        # Take Rule ID
        rid, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.rule_id_size,
                                                                                         fragment,
                                                                                         fragment_bits_left,
                                                                                         octet_index,
                                                                                         octet_bits_left)
        # Take DTag
        if self.dtag_size > 0:
            dtag, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.dtag_size,
                                                                                              fragment,
                                                                                              fragment_bits_left,
                                                                                              octet_index,
                                                                                              octet_bits_left)
        # Take W
        if self.use_windows > 0:
            w, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.w_size,
                                                                                           fragment,
                                                                                           fragment_bits_left,
                                                                                           octet_index,
                                                                                           octet_bits_left)
        # Take FCN
        fcn, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.fcn_size,
                                                                                         fragment,
                                                                                         fragment_bits_left,
                                                                                         octet_index, octet_bits_left)

        if fragment_bits_left < 8:  # Lo que queda es padding
            if fcn.get_bits().all(False) is True:
                message_type = Messages.ACK_REQUEST
            elif fcn.get_bits().all(True) is True:
                message_type = Messages.SENDER_ABORT
        else:
            if fcn.get_bits().all(True) is True:
                message_type = Messages.ALL1
                # Take MIC
                mic, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(self.mic_size,
                                                                                                 fragment,
                                                                                                 fragment_bits_left,
                                                                                                 octet_index,
                                                                                                 octet_bits_left)
                # Take Payload
                payload, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(fragment_bits_left,
                                                                                                     fragment,
                                                                                                     fragment_bits_left,
                                                                                                     octet_index,
                                                                                                     octet_bits_left)
            else:
                message_type = Messages.REGULAR
                # Take Payload
                payload, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(fragment_bits_left,
                                                                                                     fragment,
                                                                                                     fragment_bits_left,
                                                                                                     octet_index,
                                                                                                     octet_bits_left)

        headers = [rid, dtag, w, fcn, mic, payload]
        return message_type, headers

