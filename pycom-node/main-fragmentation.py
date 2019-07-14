#######################################################################
# Imports
#######################################################################

# Pycom imports
from network import LoRa
import socket
import ubinascii
import struct
import time
import math
from os import urandom

# F/R imports
from bitstring import Bits
from FREngine import FREngine
from FRBitmap import FRBitmap
from FRCommon import *
from FRFragment import FRFragmentEngine
from FRPacket import FRPacket
from FRProfile import FRProfile
from FRTile import FRTile
from uCRC32 import CRC32



#######################################################################
# Params
#######################################################################
LORA_NODE_DR = 4
PACKET_LEN_BYTES = 300
LORA_FREQUENCY = 915200000

#######################################################################
# LoRaWAN Initialization
#######################################################################

# Initialise LoRa in LORAWAN mode.
# Chile = LoRa.AU915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915, device_class=LoRa.CLASS_C)

# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260314F5'))[0]
nwk_swkey = ubinascii.unhexlify('25E66430DF07DCE2C2359BF37C64ADE7')
app_swkey = ubinascii.unhexlify('0D762F6ED62B7DB90FE627793EB0898D')

# Prepare channels
for channel in range(0, 72):
    lora.remove_channel(channel)

lora.add_channel(0, frequency=LORA_FREQUENCY, dr_min=0, dr_max=5)

# Join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# remove all the non-default channels
for i in range(1, 16):
    lora.remove_channel(i)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('main(): Not joined yet...')
print('main(): Network joined!')

# create a LoRa socket
lora_socket = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
lora_socket.setsockopt(socket.SOL_LORA, socket.SO_DR, LORA_NODE_DR)

lora_socket.setblocking(False)

#######################################################################
# Packet Creator
#######################################################################

# Select Rule ID, DTag and create packet
rule_id = 0
d_tag = 0
packet = urandom(PACKET_LEN_BYTES)

# Create profiles
profile_0 = FRProfile()
profile_0.enable_fragmentation()
profile_0.select_fragmentation_mode(mode=FRModes.ALWAYS_ACK)

profile_1 = FRProfile()
profile_1.enable_fragmentation()
profile_1.select_fragmentation_mode(mode=FRModes.ACK_ON_ERROR)

profile_2 = FRProfile()
profile_2.enable_fragmentation()
profile_2.select_fragmentation_mode(mode=FRModes.NO_ACK)

fragmentation = FREngine()
fragmentation.add_profile(0, profile_0)
fragmentation.add_profile(1, profile_1)
fragmentation.add_profile(2, profile_2)

fragmentation.initialize(data_rate=LORA_NODE_DR, packet=packet)
fragmentation.set_rule_id(0)

fragmentation._send_packet_always_ack(lora_socket)

# Get Tile length
# Get tiles
# Get fragments

# AHORA TENGO TODOS LOS FRAGMENTOS EN fragments = []
# tengo window size

# envio window
# envio dummy
# recibo ACK
    # Si ACK regular:
        # tomo bitmap
        # veo en Bitmap los fragmentos faltantes
        # envio fragmentos faltantes
        # envio dummy 
        # recibo ACK

# Select window Size


    





