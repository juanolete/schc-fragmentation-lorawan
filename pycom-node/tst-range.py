from network import LoRa
import socket
import ubinascii
import struct
import time
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


# LORA_FREQUENCY = 916800000
LORA_FREQUENCY = 915200000
LORA_NODE_DR = 4

def lora_event_callback(lora):
    print('lora_event_callback(): called')
    try:
        events = lora.events()
        if events & LoRa.TX_PACKET_EVENT:
            print("lora_event_callback(): Packet sent")
        if events & LoRa.RX_PACKET_EVENT:
            print("lora_event_callback(): Packet received")
            rx, port = s.recvfrom(256)
            if rx:
                print('Received: {}, on port {}'.format(rx, port))
    except Exception:
        print('lora_event_callback(): Exception')

# Initialise LoRa in LORAWAN mode.
# Chile = LoRa.AU915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915, device_class=LoRa.CLASS_C)

# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260314F5'))[0]
nwk_swkey = ubinascii.unhexlify('25E66430DF07DCE2C2359BF37C64ADE7')
app_swkey = ubinascii.unhexlify('0D762F6ED62B7DB90FE627793EB0898D')

# create an OTA authentication params
dev_eui = ubinascii.unhexlify('0076C3944D466714')
app_eui = ubinascii.unhexlify('70B3D57ED001AFEB')
app_key = ubinascii.unhexlify('910CA83663E227DDB7244B77F6620313')

for channel in range(0, 72):
    lora.remove_channel(channel)

lora.add_channel(0, frequency=LORA_FREQUENCY, dr_min=0, dr_max=5)

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# join a netowkr uisng OTAA
# lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key))

# set Tx callback
# lora.callback(trigger=LoRa.RX_PACKET_EVENT|LoRa.TX_PACKET_EVENT, handler=lora_event_callback)

# remove all the non-default channels
for i in range(1, 16):
    lora.remove_channel(i)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('main(): Not joined yet...')

print('main(): Network joined!')

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, LORA_NODE_DR)

# s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
print('main(): Setsockopt OK')

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
# s.setblocking(True)

# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

time.sleep(4)

##############################################################################

fragmentation = FREngine()
fragmentation.initialize(data_rate=LORA_NODE_DR)

while True:
    fragmentation._send_dummy_message(lora_socket)
    time.sleep(FRCommon.TX_TIME)

