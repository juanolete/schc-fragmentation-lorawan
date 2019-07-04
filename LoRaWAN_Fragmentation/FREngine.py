from FRPacket import FRPacket as Packet
from FRFragment import FRFragmentEngine as FragmentEngine
from FRProfile import FRProfile
import FRCommon


class FREngine:
    """
    A class used to implement the fragmentation algorithm for LoRaWAN

    Attributes
    ----------
    DR : int
        the value of the data rate using in the LoRaWAN link
    id_profiles: dict of (int, FRProfile)
        mapping of Rule ID with Profile
    packet: FRPacket
        object that contains the SCHC packet
    fragments: list of Bits
        list that contains the SCHC Regular Fragments and the SCHC All-1 Fragment
    msg_counter: int
        counter of messages transmitted

    """
    def __init__(self):
        self.DR = None
        self.id_profiles = None
        self.packet = None
        self.fragments = None
        self.msg_counter = 0
        return

    def initialize(self, data_rate: int):
        """
        Initialize the object with the (Rule ID : Profile) mapping empty and th DR value
        :param data_rate:
        :return:
        """

        self.DR = data_rate
        self.id_profiles = {}
        return

    def set_packet(self, packet: bytes):
        """
        Set the bytes packet and initialize a FRPacket object
        :param packet:
        :return:
        """

        self.fragments = []
        self.packet = Packet()
        self.packet.set_packet(packet)
        return

    def add_profile(self, rule_id: int, profile: FRProfile):
        """
        Add a profile with an specific Rule ID value
        :param rule_id: Rule ID value
        :param profile: A FRProfile defined out of the class
        :return:
        """

        if isinstance(rule_id, int):
            self.id_profiles[rule_id] = profile
        else:
            print("## Rule ID value must be an integer")
        return

    # Create all tiles and fragments
    def _compute_packet(self, rule_id: int, d_tag: int):
        """
        Function that creates the SCHC Fragments depending on the Profile information, the Rule ID and the DTag value
        It creates the SCHC Regular Fragments depending on the use of windows
        It calculates the MIC and the padding bits for the creation of the SCHC All-1 Fragment
        :param rule_id: 
        :param d_tag:
        :return:
        """

        self.fragments = []
        profile = self.id_profiles[rule_id]
        if profile.fragmentation:
            # Create Fragments Engine object
            fragment_engine = FragmentEngine(profile, rule_id, d_tag)
            # Calculate tile length
            regular_header_size = fragment_engine.regular_fragment_header_size()  # Return size in Bits
            max_fragment_size = FRCommon.DR_AUS915[self.DR]*8  # Return size in Bits
            tile_len = max_fragment_size - regular_header_size  # Return size in Bits
            # Get the tiles with the specific tile length and calculate the padding bits and MIC
            fragments_number = self.packet.get_tiles(profile, tile_len)
            pad_bits = fragment_engine.last_tile_padding(self.packet.tiles[fragments_number-1])
            self.packet.set_padding(pad_bits)
            self.packet.calculate_mic(profile)

            # Hasta aqui tengo:
            #   El total de fragmentos en fragments_number
            #   Todos los tiles en self.packet.tiles
            #   El valor del MIC en self.packet.MIC

            # Ahora debo crear los fragmentos para caso con ventanas y sin ventanas
            if profile.use_windows:
                window = 0
                fcn = profile.WINDOW_SIZE
                # Crear Regular fragments
                for tile_index in range(0, fragments_number-1):
                    if fcn < 0:
                        window += 1
                        fcn = profile.WINDOW_SIZE
                    fragment = fragment_engine.create_regular_fragment(self.packet.tiles[tile_index], window, fcn)
                    self.fragments.append(fragment)
                    fcn -= 1
                # Crear All-1 fragment
                fragment = fragment_engine.create_all_1_fragment(self.packet.tiles[fragments_number-1], self.packet.MIC,
                                                                 window)
                self.fragments.append(fragment)
            else:
                # Crear Regular fragments
                for tile_index in range(0, fragments_number-1):
                    fragment = fragment_engine.create_regular_fragment(self.packet.tiles[tile_index])
                    self.fragments.append(fragment)
                # Crear All-1 fragment
                fragment = fragment_engine.create_all_1_fragment(self.packet.tiles[fragments_number-1], self.packet.MIC)
                self.fragments.append(fragment)
        else:
            self.fragments = [self.packet.get_packet()]
        print("## All Fragments Created")
        return


