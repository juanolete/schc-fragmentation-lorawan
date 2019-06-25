from FRProfile import FRProfile as Profile
from FREngine import *
from FRCommon import *
from os import urandom

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

LoRa_DR = 7
frag_engine = FREngine()
frag_engine.initialize(DR=LoRa_DR)
frag_engine.add_profile(rule_id, profile)
frag_engine.set_packet(packet)
# frag_engine.send(rule_id, d_tag)
# frag_engine.print_stats()

print("Calculating paddin")
print(padding_bits(9,8))
print(padding_bits(10,8))
print(padding_bits(11,8))
print(padding_bits(12,8))
print(padding_bits(13,8))
print(padding_bits(14,8))
print(padding_bits(15,8))
print(padding_bits(16,8))
print(padding_bits(17,8))
print(padding_bits(18,8))
print(padding_bits(19,8))
print(padding_bits(20,8))
print(padding_bits(21,8))
print(padding_bits(22,8))
print(padding_bits(23,8))
print(padding_bits(24,8))
print(padding_bits(25,8))
print(padding_bits(26,8))
print(padding_bits(27,8))

print(lsb_mask[7])




