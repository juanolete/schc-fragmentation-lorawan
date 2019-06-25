class CRC32:

    def __init__(self):
        self.crc_table = self._create_table()

    def _create_table(self):
        a = []
        for i in range(256):
            k = i
            for j in range(8):
                if k & 1:
                    k ^= 0x1db710640
                k >>= 1
            a.append(k)
        return a

    def calc(self, buf, crc=0):
        crc ^= 0xffffffff
        for k in buf:
            crc = (crc >> 8) ^ self.crc_table[(crc & 0xff) ^ k]
        return crc ^ 0xffffffff
