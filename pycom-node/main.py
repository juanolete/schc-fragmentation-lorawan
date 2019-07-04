from network import LoRa
import socket
import ubinascii
import struct
import time
from os import urandom


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
            print(s.recv(64))
    except Exception:
        print('lora_event_callback(): Exception')

# Initialise LoRa in LORAWAN mode.
# Australia = LoRa.AU915
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915, device_class=LoRa.CLASS_C)

# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('26031557'))[0]
nwk_swkey = ubinascii.unhexlify('009224952FFC444E6BF34C3CE2A55E06')
app_swkey = ubinascii.unhexlify('136FAB6D34FF450ABD17979D3A6F9836')

# create an OTA authentication params
dev_eui = ubinascii.unhexlify('70B3D54998EA22BD')
app_eui = ubinascii.unhexlify('70B3D57ED001AFEB')
app_key = ubinascii.unhexlify('910CA83663E227DDB7244B77F6620313')

for channel in range(0, 72):
    lora.remove_channel(channel)

lora.add_channel(0, frequency=LORA_FREQUENCY, dr_min=0, dr_max=5)

# prepare_channels(lora, 64, 3)
# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))

# join a netowkr uisng OTAA
# lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key))

# set Tx callback
# lora.callback(trigger=LoRa.RX_PACKET_EVENT ,handler=lora_event_callback)

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
# Preparing Data

from bitstring import Bits
from FRPacket import FRPacket as Packet
packet_len = 1380  # bytes
tile_len = 216 * 8
tst_packet = Packet()
tst_packet.random_generate(packet_len)
tst_packet.always_ack_get_tiles(tile_len)

message_bits = tst_packet.tiles[0].get_bits()
print("Message: ", message_bits.hex)
#############################################################################################

# send some data
try:
    # s.send(bytes([0x01, 0x02, 0x03]))
    s.send(message_bits.tobytes())
    print('main(): Send OK')
    time.sleep(4)
    rx, port = s.recvfrom(256)
    if rx:
        print('Received: {}, on port {}'.format(rx, port))
    time.sleep(6)
except OSError as e:
    print('ERROR')
    print(e.args[0])
    # if e.args[0] == 11:
'''
# get any data received (if any...)
data = s.recv(256)
print(data)
'''
print("END")
