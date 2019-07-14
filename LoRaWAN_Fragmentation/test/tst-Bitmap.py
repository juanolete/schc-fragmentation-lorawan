from FRBitmap import FRBitmap as Bitmap
from bitstring import Bits


window_size = 7
bmp = Bitmap(window_size)
print(bmp.bitmap)
bmp.set_bit_by_fcn(0,True)
bmp.set_bit_by_fcn(1,True)
bmp.set_bit_by_fcn(2,True)
bmp.set_bit_by_fcn(4,True)
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

new_bmp = Bitmap(window_size)
new_bmp.set_bit_by_fcn(6, True)
#new_bmp.set_bit_by_fcn(5, True)
# new_bmp.set_bit_by_fcn(4, True)


null_bmp = Bitmap(0)

print(bmp.equals(null_bmp))

bits = Bits(bin="1001")
bmp.set_from_bits(bits)

new_bmp.set_last_unsent()
print("New bmp: ", new_bmp.bitmap)


