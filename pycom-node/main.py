from network import LoRa
import socket
import time
import ubinascii
import struct
from ubitstring import Bits as bits

import FREngine




###############################################################################
############################# LoRa Basic Send #################################
###############################################################################

'''
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
lora = LoRa(mode=LoRa.LORAWAN, region=LoRa.AU915, frequency=916800000, sf=12,)

for channel in range(0, 72):
    lora.add_channel(channel, frequency=916800000, dr_min=0, dr_max=0)

# create an OTAA authentication parameters
dev_eui = ubinascii.unhexlify('70B3D5499F71073F')
app_eui = ubinascii.unhexlify('70B3D57ED001AFEB')
app_key = ubinascii.unhexlify('281B44C0085F372EB4B21FAA71B82113')

# join a network using OTAA (Over the Air Activation)
lora.join(activation=LoRa.OTAA, auth=(dev_eui, app_eui, app_key), timeout=0)

# create an ABP authentication params
dev_addr = struct.unpack(">l", ubinascii.unhexlify('260318D0'))[0]
nwk_swkey = ubinascii.unhexlify('DB2B131BAB37459ABD872695306CECA9')
app_swkey = ubinascii.unhexlify('4DB274AA49361A18C4457AEFBB1B5E1B')

# join a network using ABP (Activation By Personalization)
lora.join(activation=LoRa.ABP, auth=(dev_addr, nwk_swkey, app_swkey))
lora.callback(trigger=LoRa.TX_PACKET_EVENT,handler=lora_event_callback)

# wait until the module has joined the network
while not lora.has_joined():
    time.sleep(2.5)
    print('Not yet joined...')

print('Network joined!')

# create a LoRa socket
s = socket.socket(socket.AF_LORA, socket.SOCK_RAW)

# set the LoRaWAN data rate
s.setsockopt(socket.SOL_LORA, socket.SO_DR, 0)
#s.setsockopt(socket.SOL_LORA, socket.SO_CONFIRMED, True)
print('Setseckopt OK')

# make the socket blocking
# (waits for the data to be sent and for the 2 receive windows to expire)
#s.setblocking(True)

# send some data
uno = bits(uint = 10, length = 8)
dos = bits(uint = 5, length = 8)
tres = bits(uint = 8, length = 8)
data = uno + dos + tres
print(data)

try:
    s.setblocking(True)
    s.send(data.tobytes())
    print('Send OK')

except OSError as e:
    print(e.args[0])


while True:
    s.setblocking(True)
    
    a = bytes([0x01, 0x02, 0x03])
    s.send(a)
    s.setblocking(False)
    #data = s.recv(255)
    #print(data)
    time.sleep(2)

# make the socket non-blocking
# (because if there's no data received it will block forever...)


# get any data received (if any...)

'''





###############################################################################
################################ FRAGMENTATION ################################
###############################################################################

###################
#TESTS
###################

import FRConstants
import FRPacket
import FRProfile
import FRRuleId
import FRFragment
import FRWindow

from FRConstants import *
from FRPacket import FRPacket as Packet
from FRProfile import FRProfile as Profile
from FRRuleId import FRRuleID as RuleId
from FRFragment import FRFragment as Fragment
from FRWindow import FRWindow as Window

engine = FREngine()
profile = Profile()
ruleId = RuleId(1, profile)
packet = Packet()
engine.initilialize()
engine.set_profile(profile)
engine.set_ruleId(ruleId)
engine.set_packet(packet)
engine.begin_fragmentation()