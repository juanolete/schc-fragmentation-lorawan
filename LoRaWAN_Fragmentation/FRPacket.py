class FRPacket:

    def __init__(self, packet):
        self._packet = packet #bytes array
        self._tiles = None #
        self._fragments = None
        return

    def get_tiles(self, largo_tile):
        self._tiles = []
        tile = []
        # verificar si el tamaño de packet es multiplo del tamaño de tile
        if bitsPacket.length % tileLengthBits > 0:
            # no es multiplo -> agregar padding
            padding = tileLengthBits - bitsPacket.length % tileLengthBits
            bitsPacketPadding = bitsPacket + Bits(padding)
        initIndex = 0
        finalIndex = tileLengthBits
        paddedPacketLength = bitsPacketPadding.length
        while finalIndex <= paddedPacketLength:
            tile = bitsPacketPadding[initIndex:finalIndex]
            tiles.append(tile)
            initIndex += tileLengthBits
            finalIndex += tileLengthBits
        return tiles, padding