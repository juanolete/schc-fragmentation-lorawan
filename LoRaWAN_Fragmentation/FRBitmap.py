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

    def compare(self, new_bitmap):
        if self.size != new_bitmap.size:
            return False
        for index in range(0, self.size):
            if self.bitmap[index] != new_bitmap.bitmap[index]:
                return False
        return True

