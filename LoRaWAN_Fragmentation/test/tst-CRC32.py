from uCRC32 import *
from bitstring import Bits
from os import urandom

A = Bits(hex='abcd123')
B = Bits(hex='1234abcd')

C = bytes([1, 2, 3, 4, 5, 6])
D = urandom(1000)

print("CRC A: ", CRC32().calc(D))





