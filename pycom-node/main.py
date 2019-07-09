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
print("\n")
#############################################################################################

# send some data

def _send_bits_uplink(socket: socket, data: Bits): 
    print("## Sending msg: ", data.hex)
    socket.send(data.tobytes())

def _receive_downlink(socket: socket):
    rx, port = socket.recvfrom(256)
    if rx:
        print("Received: {}, on port {}".format(rx,port))
    return rx

TX_WAIT = 5
RX_WAIT = 4

try:
    # s.send(bytes([0x01, 0x02, 0x03]))
    print("Message: ", message_bits.tobytes())
    print("\n")

    print("Sending 1")

    _send_bits_uplink(s, message_bits)
    #s.send(message_bits.tobytes())
    time.sleep(RX_WAIT)
    rx = _receive_downlink(s)
    if rx: 
        print(rx)
    time.sleep(TX_WAIT)

    print("Sending 2")
    #s.send(tst_packet.tiles[1].get_bits().tobytes())
    _send_bits_uplink(s, tst_packet.tiles[1].get_bits())
    time.sleep(RX_WAIT)
    rx = _receive_downlink(s)
    if rx: 
        print(rx)
    time.sleep(TX_WAIT)

    print("Sending 3")
    #s.send(tst_packet.tiles[2].get_bits().tobytes())
    _send_bits_uplink(s, tst_packet.tiles[2].get_bits())
    time.sleep(RX_WAIT)
    rx = _receive_downlink(s)
    if rx: 
        print(rx)
    time.sleep(TX_WAIT)

    print("Sending 4")
    _send_bits_uplink(s, tst_packet.tiles[3].get_bits())
    #s.send(tst_packet.tiles[3].get_bits().tobytes())
    time.sleep(RX_WAIT)
    rx = _receive_downlink(s)
    if rx: 
        print(rx)
    time.sleep(TX_WAIT)

    print("Sending 5")
    _send_bits_uplink(s, tst_packet.tiles[4].get_bits())
    #s.send(tst_packet.tiles[4].get_bits().tobytes())
    time.sleep(RX_WAIT)
    rx = _receive_downlink(s)
    if rx: 
        print(rx)

    '''
    print('main(): Send OK')
    time.sleep(4)
    rx, port = s.recvfrom(256)
    if rx:
        print('Received: {}, on port {}'.format(rx, port))
    time.sleep(2)
    '''
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
