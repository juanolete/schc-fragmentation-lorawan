from bitstring import Bits
from FRCommon import take_field_from_fragment

rid = Bits(bin='011')
dtag = Bits(uint=1, length=1)
w = Bits(uint=1, length=1)
fcn = Bits(uint=3, length=3)
tile = Bits(bin='0b11100011')
padding = Bits(bin='00')

fragment = rid + dtag + w + fcn + tile + padding

c = Bits(uint=1, length=1)

ack = rid + dtag + w + c

print("Fragment: " ,fragment.bin)
RID, frag_bits_left, oct_index, oct_bits_left = take_field_from_fragment(3, fragment.tobytes(), len(fragment.tobytes())*8, 0, 8)
DTAG, frag_bits_left, oct_index, oct_bits_left = take_field_from_fragment(1, fragment.tobytes(), frag_bits_left, oct_index, oct_bits_left)
W, frag_bits_left, oct_index, oct_bits_left = take_field_from_fragment(1, fragment.tobytes(), frag_bits_left, oct_index, oct_bits_left)
FCN, frag_bits_left, oct_index, oct_bits_left = take_field_from_fragment(3, fragment.tobytes(), frag_bits_left, oct_index, oct_bits_left)
TILE, frag_bits_left, oct_index, oct_bits_left = take_field_from_fragment(8, fragment.tobytes(), frag_bits_left, oct_index, oct_bits_left)

print("Rule ID: ", RID.get_bits().bin)
print("DTAG: ",DTAG.get_bits().bin)
print("W: ",W.get_bits().bin)
print("FCN: ",FCN.get_bits().bin)
print("TILE: ",TILE.get_bits().bin)
print("Fragment Bits Left: ", frag_bits_left)
r_fragment = RID.get_bits() + DTAG.get_bits() + W.get_bits() + FCN.get_bits() + TILE.get_bits() + padding
print("FRAGMENT REASSEMBLED: ",r_fragment.bin)

assert fragment == r_fragment

