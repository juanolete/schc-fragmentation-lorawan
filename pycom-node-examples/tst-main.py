from network import LoRa
import socket
import ubinascii
import struct
import time
from uos import urandom


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
lora = LoRa(mode=LoRa.LORAWAN,region=LoRa.AU915)

# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('2603179A'))[0]
nwk_swkey = ubinascii.unhexlify('30AD7EDF15AFB4948A94F19840171481')
app_swkey = ubinascii.unhexlify('2504CE1065E4ABD41E1ABF0726AE0EEA')

for channel in range(0, 72):
    lora.add_channel(channel, frequency=916800000, dr_min=0, dr_max=7)

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
lora.callback(trigger=LoRa.TX_PACKET_EVENT,handler=lora_event_callback)
# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('main(): Not joined yet...')

print('main(): Network joined!')

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
#s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
print('main(): Setsockopt OK')

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
s.setblocking(True)

# send some data
try:
    # s.send(bytes([0x01, 0x02, 0x03]))
    s.send(urandom(1))
    print('main(): Send OK')
except OSError as e:
    print('ERROR')
    print(e.args[0])
    # if e.args[0] == 11:

'''
# make the socket non-blocking
# (because if there's no data received it will block forever...)
s.setblocking(False)

# # get any data received (if any...)
data = s.recv(64)
print(data)
'''