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