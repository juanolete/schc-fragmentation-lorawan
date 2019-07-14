from bitstring import Bits

class FRBitmap:

    def __init__(self, window_size: int):
        self.size = window_size
        self.bitmap = [0] * window_size

    def set_bit_by_fcn(self, fcn: int, value: bool):
        self.bitmap[fcn] = int(value)

    def set_bit_by_sent_order(self, sent_order: int, value: bool):
        self.bitmap[-sent_order-1] = int(value)

    def get_value(self):
        value = 0
        for index in range(0, self.size):
            if self.bitmap[index]:
                value += (1 << index)
        return value

    def get_value_msb(self, number_of_msb):
        value = 0
        for index in range(0, self.size):
            if self.bitmap[index]:
                value += (1 << index)
        return value >> (self.size - number_of_msb)

    def get_msb_to_take(self):
        value = self.get_value()
        msb_to_take = self.size
        mask = 0b01
        while value & mask:
            value = value >> 1
            msb_to_take -= 1
        return msb_to_take

    def get_missing_fragments(self):
        missing_fragments = 0
        for fragment_sent in self.bitmap:
            if not fragment_sent:
                missing_fragments += 1
        return missing_fragments

    def get_missing_fragments_until(self, fcn):
        missing_fragments = 0
        index = self.size-1
        while index >= fcn:
            fragment_sent = self.bitmap[index]
            if not fragment_sent:
                missing_fragments += 1
            index -= 1
        return missing_fragments

    def get_sent_fragments(self):
        return self.size - self.get_missing_fragments()

    def equals(self, new_bitmap):
        if self.size != new_bitmap.size:
            return False
        for index in range(0, self.size):
            if self.bitmap[index] != new_bitmap.bitmap[index]:
                return False
        return True

    def set_from_bits(self, bits: Bits):
        bits_difference = self.size - bits.len
        bitmap_value = bits.int
        if bits_difference < 0:
            print("Bits object is too big")
        elif bits_difference == 0:
            self.set_from_int(bitmap_value)
        else:
            for index in range(0, bits_difference):
                bitmap_value = (bitmap_value << 1) | 0b1
            self.set_from_int(bitmap_value)

    def set_from_int(self, value: int):
        for index in range(0, self.size):
            self.bitmap[index] = value & 0b1
            value = value >> 1

    def set_last_unsent(self):
        index = self.size-1
        while index >= 0:
            if not self.bitmap[index]:
                self.bitmap[index] = 1
                return
            index -= 1
        return
