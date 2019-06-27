from bitstring import Bits


class FRTile:
    def __init__(self, length):
        self.bytes = []
        self.length = []
        self.max_len = length
        self.emptyBits = length
        self.fullBits = 0
        return

    def add_byte(self, new_byte, length):
        if self.emptyBits < length:
            print("## Empty space of Tile is not enough")
            return
        self.bytes.append(new_byte)
        self.length.append(length)
        self.emptyBits -= length
        self.fullBits += length
        return

    def get_bits(self):
        tile = None
        for index in range(0, len(self.bytes)):
            new_tile = Bits(uint=self.bytes[index], length=self.length[index])
            tile += new_tile
        return tile
