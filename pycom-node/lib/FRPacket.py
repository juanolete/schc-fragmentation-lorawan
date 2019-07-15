import math
from os import urandom
from bitstring import Bits
from FRCommon import FRModes as Modes
from FRCommon import lsb_mask
from FRCommon import take_field_from_fragment
from FRTile import FRTile as Tile
from FRProfile import FRProfile as Profile
from uCRC32 import CRC32


class FRPacket:

    def __init__(self):
        self.packet = None
        self.tiles = []
        self.packet_padding = None
        self.last_tile_padding = None
        self.MIC = None
        return

    def set_packet(self, packet):
        self.packet = packet
        return

    def set_tiles(self, tiles):
        self.tiles = tiles.copy()
        return

    def get_packet(self):
        return self.packet

    def random_generate(self, length_in_bytes):
        self.packet = urandom(length_in_bytes)
        return

    def set_padding(self, bits):
        self.last_tile_padding = bits
        if bits == 0:
            self.packet_padding = bytes(0)
        else:
            self.packet_padding = bytes(1)

    def calculate_mic(self, profile):
        if profile.mic_algo == 'CRC32':
            self.MIC = CRC32().calc(self.packet + self.packet_padding)
            return

    def get_tiles(self, profile: Profile, tile_len: int):
        if profile.mode == Modes.NO_ACK:
            return self.no_ack_get_tiles(tile_len, profile.l2_word_size)
        elif profile.mode == Modes.ALWAYS_ACK:
            return self.always_ack_get_tiles(tile_len, profile.l2_word_size)
        elif profile.mode == Modes.ACK_ON_ERROR:
            return self.ack_on_error_get_tiles(tile_len, profile.penultimate_tile_smaller, profile.l2_word_size)

    def no_ack_get_tiles(self, tile_len, l2_size=8):
        return self.always_ack_get_tiles(tile_len, l2_size)

    def ack_on_error_get_tiles(self, tile_len, penultimate_tile_small=False, l2_size=8):
        return

    def always_ack_get_tiles(self, tile_len, l2_size=8):
        packet_bits = len(self.packet)*8
        max_tiles = 0
        # Get number of tiles
        if tile_len < l2_size:
            print("## Tile length must be equal or greater than L2 size word =", l2_size)
        else:
            remainder_tile = 0
            if packet_bits % tile_len > 0:
                remainder_tile = 1
            max_tiles = math.floor(packet_bits / tile_len) + remainder_tile
        # Get tiles
        packet_bits_left = packet_bits
        all_tiles = []
        tile = None
        octet_bits_left = 8
        octet_index = 0
        while packet_bits_left > 0:
            tile, packet_bits_left, octet_index, octet_bits_left = take_field_from_fragment(tile_len,
                                                                                            self.packet,
                                                                                            packet_bits_left,
                                                                                            octet_index,
                                                                                            octet_bits_left)
            all_tiles.append(tile)
        if len(all_tiles) != max_tiles:
            print("## Error in number of Tiles created")
        else:
            self.tiles = all_tiles
            print("## Tiles created")
        return max_tiles

    def construct_from_tiles(self, all_tiles):
        tiles_number = len(all_tiles)
        packet = Bits(0)
        for tiles_index in range(0, tiles_number):
            packet = packet + all_tiles[tiles_index].get_bits()
        self.packet = packet.tobytes()
        self.tiles = all_tiles
        return

    def add_window_to_packet(self, window):
        index = len(window) - 1
        while index >= 0:
            if window[index] is not None:
                self.tiles.append(window[index])
            index -= 1
        return

