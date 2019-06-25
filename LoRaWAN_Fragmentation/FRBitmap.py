class FRBitmap:

    def __init__(self, window_size: int):
        self.size = window_size
        self.bitmap = [False] * window_size

    def set_bit(self, fcn: int, value: bool):
        self.bitmap[fcn] = value

    def get_bits(self):
        value = 0
        for bit in range(0, self.size):
            pass

