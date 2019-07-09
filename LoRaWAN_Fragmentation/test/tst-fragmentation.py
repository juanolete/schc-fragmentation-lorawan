from FRProfile import FRProfile as Profile
from FREngine import *
import math
from os import urandom
from FRBitmap import FRBitmap as Bitmap
from bitstring import Bits
# Parameters for test
rule_id = 0
packet_len = 1000
d_tag = 0

# Profile creation
profile = Profile()
profile.select_fragmentation_mode(mode='ALWAYS_ACK')
profile.enable_fragmentation()

# Packet generator
packet = urandom(1000)

LoRa_DR = 0
frag_engine = FREngine()
frag_engine.add_profile(rule_id, profile)
frag_engine.initialize(data_rate=LoRa_DR, packet=packet)
windows_number = frag_engine.compute_packet(rule_id, d_tag)
print("N° Windows: ", windows_number)


def _send_window(fragments, init_index, window_size, bitmap: Bitmap):
    if window_size != bitmap.size:
        print("## Bitmap size do not correspond with WINDOW_SIZE")
        return
    fragments_number = len(fragments)
    fragment_index = init_index
    reversed_bitmap = bitmap.bitmap[::-1]
    for index in range(0, bitmap.size):
        if fragment_index >= fragments_number:
            return fragment_index
        else:
            fragment_sent = reversed_bitmap[index]
            if not fragment_sent:
                print("Enviando fragmento: ", fragment_index)
                # Send fragment_index
                bitmap.set_bit_by_sent_order(index, True)
                # sleep
                pass
            fragment_index += 1
    return fragment_index

bmp = Bitmap(profile.WINDOW_SIZE)
bmp.set_bit_by_sent_order(2, True)
bmp.set_bit_by_sent_order(4, True)
print(bmp.bitmap)
_send_window(frag_engine.fragments, 0, profile.WINDOW_SIZE, bmp)

print(bmp.bitmap)
def _send_last_window(fragments, init_index, window_size):
    pass





