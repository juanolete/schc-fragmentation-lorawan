import math
from os import urandom
from FRCommon import FRModes as Modes
from FRCommon import lsb_mask
from FRTile import FRTile as Tile
from uCRC32 import CRC32


class FRPacket:

    def __init__(self):
        self.packet = None
        self.tiles = None
        self.packet_padding = None
        self.last_tile_padding = None
        self.MIC = None
        return

    def set_packet(self, packet):
        self.packet = packet
        return

    def get_packet(self):
        return self.packet

    def random_generate(self, length):
        self.packet = urandom(length)
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

    def get_tiles(self, profile, tile_len):
        if profile.mode == Modes.NO_ACK:
            self.no_ack_get_tiles(tile_len, profile.l2_word_size)
        elif profile.mode == Modes.ALWAYS_ACK:
            self.always_ack_get_tiles(tile_len, profile.l2_word_size)
        elif profile.mode == Modes.ACK_ON_ERROR:
            self.ack_on_error_get_tiles(tile_len, profile.penultimate_tile_smaller, profile.l2_word_size)
        return

    def always_ack_get_tiles(self, tile_len, l2_size=8):
        packet_bits = len(self.packet) * 8
        max_tiles = 0
        # Get number of tiles
        if tile_len < l2_size:
            print("## Tile length must be equal or greater than L2 size word =", l2_size)
        else:
            remainder_tile = 0
            if packet_bits % tile_len > 0:
                remainder_tile = 1
            max_tiles = math.floor(packet_bits / tile_len) + remainder_tile
        # Create tiles
        packet_bits_left = packet_bits
        all_tiles = []
        # Estado incial, all_tiles vacio, tile vacia, indice 0
        tile = Tile(tile_len)  # Se crea nueva Tile con un espacio libre de [tile_len] bits
        octet_bits_left = 8  # Se pueden tomar los 8bits
        octet_index = 0
        while packet_bits_left > 0:
            if tile.emptyBits >= 8:
                if octet_bits_left == 8:
                    tile.add_byte(self.packet[octet_index], octet_bits_left)
                else:
                    # auxByte = bytes_to_int(packet[octet_index]) & lsb_mask[octet_bits_left]
                    # tile.addByte(bytes([auxByte]), octet_bits_left)
                    aux_byte = self.packet[octet_index] & lsb_mask[octet_bits_left]
                    tile.add_byte(aux_byte, octet_bits_left)
                packet_bits_left -= octet_bits_left
                octet_bits_left = 8
                octet_index += 1
            else:
                taken_bits = tile.emptyBits
                # auxByte = (bytes_to_int(packet[octet_index])) >> (8 - takenBits)
                # tile.addByte(bytes([auxByte]), takenBits)
                aux_byte = self.packet[octet_index] >> (8 - taken_bits)
                tile.add_byte(aux_byte, taken_bits)
                packet_bits_left -= taken_bits
                octet_bits_left -= taken_bits
            if tile.emptyBits == 0 and packet_bits_left > 0:
                all_tiles.append(tile)
                tile = Tile(tile_len)
        # Append the last tile
        all_tiles.append(tile)
        if len(all_tiles) != max_tiles:
            print("## Error in number of Tiles created")
        else:
            self.tiles = all_tiles
        return

    def no_ack_get_tiles(self, tile_len, l2_size=8):
        self.always_ack_get_tiles(tile_len, l2_size)
        return

    def ack_on_error_get_tiles(self, tile_len, penultimate_tile_small=False, l2_size=8):
        return
