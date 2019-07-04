from network import LoRa
import socket
import time
import ubinascii
import struct

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

################################ FRPacket ##################################################
'''
from bitstring import Bits
from FRPacket import FRPacket as Packet
packet_len = 1380  # bytes
tile_len = 222
tst_packet = Packet()
tst_packet.random_generate(packet_len)
tst_packet.always_ack_get_tiles(tile_len)

print("Numero de Tiles: ", len(tst_packet.tiles))
print("Numero de bits en tiles (excepto la ultima): ", (len(tst_packet.tiles)-1)*tile_len)
print("Bits en last Tile: ", tst_packet.tiles[len(tst_packet.tiles)-1].fullBits)
print("Packet bits: ", packet_len*8)

tiles = tst_packet.tiles
recovery_packet = Packet()
recovery_packet.construct_from_tiles(tiles)

assert tst_packet.packet == recovery_packet.packet
'''
############################################################################################

############################## FRBitmap ####################################################
'''
from FRBitmap import FRBitmap as Bitmap
from bitstring import Bits


window_size = 7
bmp = Bitmap(window_size)
print(bmp.bitmap)
bmp.set_bit(0,True)
bmp.set_bit(1,True)
bmp.set_bit(2,True)
bmp.set_bit(4,True)
print(bmp.bitmap)
print((Bits(uint=bmp.get_value(),length=bmp.size)).bin)

msb_to_take = bmp.get_msb_to_take()
print(msb_to_take)

msb_number = 4
bmp_bits = Bits(uint=bmp.get_value_msb(msb_number), length=msb_number)
print(bmp_bits.bin)
index = bmp_bits.len-1
while index >= 0:
    print("BIT : ", bmp_bits[index])
    index -= 1

'''
################################################################################################

##################################### CRC32 ####################################################
'''
from uCRC32 import *
from bitstring import Bits
from os import urandom

C = bytes([1, 2, 3, 4, 5, 6])
D = urandom(1000)

print("CRC A: ", CRC32().calc(C))
'''
################################################################################################

###################################### Field Recovery ##########################################
'''
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
'''
##########################################################################################################

######################################### Messages ################################################

'''
from FRFragment import FRFragmentEngine as FragmentEngine
from FRProfile import FRProfile as Profile
from FRPacket import FRPacket as Packet
from FRBitmap import FRBitmap as Bitmap
from FRCommon import *

profile = Profile()
profile.select_fragmentation_mode(FRModes.ALWAYS_ACK)
profile.enable_fragmentation()

fragment_engine = FragmentEngine(profile, 0, 1)

tile_len = 50*8
packet_len = 1380
packet = Packet()
packet.random_generate(packet_len)
# packet.set_packet(packet_bytes)
packet.get_tiles(profile, tile_len)

print("Rule ID Size: ", profile.rule_id_size)
print("DTag Size: ", profile.dtag_size)
print("W Size: ", profile.w_size)
print("FCN Size: ", profile.fcn_size)

print("## Prueba para Receiver")
all1 = fragment_engine.create_all_1_fragment(packet.tiles[0], 303397878)
ack_req = fragment_engine.create_ack_req(0)
sender_abort = fragment_engine.create_sender_abort()
regular = fragment_engine.create_regular_fragment(packet.tiles[0])

message_type, headers = fragment_engine.receiver_message_recovery(all1.tobytes())
print(message_type)
message_type, headers = fragment_engine.receiver_message_recovery(ack_req.tobytes())
print(message_type)
message_type, headers = fragment_engine.receiver_message_recovery(sender_abort.tobytes())
print(message_type)
message_type, headers = fragment_engine.receiver_message_recovery(regular.tobytes())
print(message_type)

print("## Prueba para Sender")
bmp = Bitmap(profile.WINDOW_SIZE)
ack = fragment_engine.create_ack(bmp)
receiver_abort = fragment_engine.create_receiver_abort()

message_type, headers = fragment_engine.sender_message_recovery(ack.tobytes())
print(message_type)
message_type, headers = fragment_engine.sender_message_recovery(receiver_abort.tobytes())
print(message_type)

'''