from FRBitmap import FRBitmap as Bitmap
from bitstring import Bits


window_size = 7
bmp = Bitmap(window_size)
print(bmp.bitmap)
bmp.set_bit(0,True)
bmp.set_bit(1,True)
bmp.set_bit(2,True)
bmp.set_bit(4,True)
print(bmp.bitmap)
print((Bits(uint=bmp.get_value(),length=bmp.size)).bin)

msb_to_take = bmp.get_msb_to_take()
print(msb_to_take)

msb_number = 4
bmp_bits = Bits(uint=bmp.get_value_msb(msb_number), length=msb_number)
print(bmp_bits.bin)
index = bmp_bits.len-1
while index >= 0:
    print("BIT : ", bmp_bits[index])
    index -= 1

print("Missing fragments: ", bmp.get_missing_fragments())