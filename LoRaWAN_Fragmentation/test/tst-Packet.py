from bitstring import Bits


packet_bytes = bytearray([232, 124, 55, 2, 199, 13])
#packet: [11101000, 01111100, 00110111, 00000010, 11000111, 00001101]
from FRPacket import FRPacket as Packet

tile_len = 50*8
packet_len = 1380
packet = Packet()
packet.random_generate(packet_len)
#packet.set_packet(packet_bytes)
packet.always_ack_get_tiles(tile_len)

print("Numero de Tiles: ", len(packet.tiles))
print("Numero de bits en tiles (excepto la ultima): ", (len(packet.tiles)-1)*tile_len)
print("Bits en last Tile: ", packet.tiles[len(packet.tiles)-1].fullBits)
print("Packet bits: ", packet_len*8)

print("END")