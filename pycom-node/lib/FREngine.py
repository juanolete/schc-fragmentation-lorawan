from FRPacket import FRPacket as Packet
from FRFragment import FRFragmentEngine as FragmentEngine
from FRProfile import FRProfile
from FRBitmap import FRBitmap as Bitmap
from bitstring import Bits
from math import ceil
from binascii import b2a_base64
from binascii import hexlify
import FRCommon
import time


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
    """
    def __init__(self):
        self.DR = None
        self.id_profiles = {}
        self.packet = None
        self.fragments = None
        self.msg_counter_sender = 0
        self.msg_counter_receiver = 0

        self.actual_id = None
        self.actual_dtag = None

        # Only for receiver use
        self.receiving = False
        self.window = None
        self.actual_frag_engine = None
        self.actual_window = None
        self.actual_bitmap = None
        self.ack_bitmap = None
        self.send_ack = False
        self.receiving_mode = None
        self.receiving_buffer = None
        return

    def initialize(self, data_rate=None, packet=None):
        if data_rate is not None:
            self.DR = data_rate
        if packet is not None:
            self.actual_dtag = 0
            self.packet = Packet()
            self.packet.set_packet(packet)
        return

    def set_dr(self, data_rate):
        self.DR = data_rate
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
        if self.actual_dtag is not None:
            self.actual_dtag += 1
        else:
            self.actual_dtag = 0
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
    def compute_packet(self, rule_id: int, d_tag: int):
        """
        Function that creates the SCHC Fragments depending on the Profile information, the Rule ID and the DTag value
        It creates the SCHC Regular Fragments depending on the use of windows
        It calculates the MIC and the padding bits for the creation of the SCHC All-1 Fragment
        :param rule_id: 
        :param d_tag:
        :return:
        """
        windows_number = None
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
        print("## All Tiles Created")
        if (profile.use_windows is not None) and (profile.use_windows is True):
            windows_number = ceil(len(self.packet.tiles)/profile.WINDOW_SIZE)
        else:
            windows_number = 1
        print("## Windows number: ", windows_number)
        return windows_number

    def begin_window_reception(self, rule_id, dtag, window_size):
        self.window = [0] * window_size
        self.receiving = True
        self.actual_dtag = dtag
        self.actual_id = rule_id

    def end_reception(self):
        self.window = None
        self.receiving = False

    def set_rule_id(self, rule_id):
        if rule_id in self.id_profiles:
            self.actual_id = rule_id
        else:
            print("This Rule ID does not have a Profile, please add a Profile with this Rule ID first")

    def new_dtag(self):
        self.actual_dtag += 1

    def send_window(self, lora_socket, window_number: int, window_bmp: Bitmap):
        profile = self.id_profiles[self.actual_id]
        fragment_engine = FragmentEngine(profile, self.actual_id, self.actual_dtag)
        if profile.WINDOW_SIZE != window_bmp.size:
            print("## Bitmap size does not correspond with WINDOW_SIZE")
            return False
        tiles_number = len(self.packet.tiles)
        tile_index = window_number*profile.WINDOW_SIZE
        fcn = profile.WINDOW_SIZE-1
        messages_sent = 0
        while fcn >= 0:
            print("Creating fragment with W={} and FCN={}".format(window_number, fcn))
            fragment = None
            if tile_index >= tiles_number:
                return False
            else:
                fragment_sent = window_bmp.bitmap[fcn]
                if not fragment_sent:
                    if tile_index == tiles_number-1:
                        print("## Creating an All-1 fragment")
                        print("## MIC: ", self.packet.MIC)
                        fragment = fragment_engine.create_all_1_fragment(self.packet.tiles[tile_index],
                                                                         self.packet.MIC,
                                                                         window_number)
                    else:
                        print("## Creating a Regular Fragment")
                        fragment = fragment_engine.create_regular_fragment(self.packet.tiles[tile_index],
                                                                           window_number,
                                                                           fcn)
                    self.send_fragment(lora_socket, fragment)
                    self.msg_counter_sender += 1
                    messages_sent += 1
                    window_bmp.set_bit_by_fcn(fcn, True)
                    if self.receive_abort(lora_socket, fragment_engine, "SENDER"):
                        print("## Aborting packet sending")
                        return False
                    time.sleep(FRCommon.TX_TIME)
            fcn -= 1
            tile_index += 1
        return messages_sent

    def send_fragment(self, lora_socket, fragment: Bits):
        print("## Sending fragment: ", fragment.hex)
        lora_socket.send(fragment.tobytes())
        return

    def receive_abort(self, lora_socket, fragment_engine, comm_subject):
        time.sleep(FRCommon.RX_TIME)
        rx, port = lora_socket.recvfrom(256)
        if rx:
            print("## Received: {}, on port {}".format(rx, port))
            if comm_subject == "SENDER":
                message_type, headers = fragment_engine.sender_message_recovery(rx)
                if message_type == FRCommon.FRMessages.RECEIVER_ABORT:
                    print("## Received RECEIVER-ABORT message")
                    return True
            elif comm_subject == "RECEIVER":
                message_type, headers = fragment_engine.receiver_message_recovery(rx)
                if message_type == FRCommon.FRMessages.SENDER_ABORT:
                    print("## Received SENDER-ABORT message")
                    return True
        return False

    def _send_dummy_message(self, lora_socket):
        print("## Sending DUMMY message")
        lora_socket.send(FRCommon.DUMMY_MESSAGE)
        return

    def sender_receive(self, lora_socket, fragment_engine):
        time.sleep(FRCommon.RX_TIME)
        rx, port = lora_socket.recvfrom(256)
        if rx:
            print("## Received: {}, on port {}".format(rx, port))
            print("ACK Received: ", hexlify(rx))
            message_type, headers = fragment_engine.sender_message_recovery(rx)
            return message_type, headers
        else:
            return None, None

    def _sender_receive_ack_always_process(self, lora_socket, fragment_engine: FragmentEngine, profile: FRProfile,
                                           actual_window: int, windows_number: int, messages_sent: int, attempts: int,
                                           bmp: Bitmap):
        message_type, headers = None, None
        new_attempts = attempts
        new_actual_window = actual_window
        new_bmp = bmp
        # Wait for an ACK
        self._send_dummy_message(lora_socket)
        message_type, headers = self.sender_receive(lora_socket, fragment_engine)
        state = None
        if message_type == FRCommon.FRMessages.RECEIVER_ABORT:
            print("## Received a RECEIVER-ABORT message")
            print("## EXIT sending process")
            state = "ERROR"
        elif message_type == FRCommon.FRMessages.ACK:
            self.msg_counter_receiver += 1
            rec_rid = headers[FRCommon.FRHeaders.R_ID].get_bits()
            rec_dtag = headers[FRCommon.FRHeaders.D_TAG].get_bits()
            if (rec_rid.uint != self.actual_id) or (rec_dtag.uint != self.actual_dtag):
                print("Rule ID or D Tag not expected")
                return
            rec_w = headers[FRCommon.FRHeaders.W].get_bits()
            rec_c = headers[FRCommon.FRHeaders.C].get_bits()
            rec_bmp_bits = headers[FRCommon.FRHeaders.COMP_BMP].get_bits()
            rec_bmp = Bitmap(profile.WINDOW_SIZE)
            rec_bmp.set_from_bits(rec_bmp_bits)
            expected_w = actual_window & FRCommon.lsb_mask[profile.w_size]
            print("## Expected W={} ; Recover W={}".format(expected_w, rec_w.uint))
            if (expected_w) == rec_w.uint:
                if actual_window == windows_number - 1:
                    if rec_bmp.get_sent_fragments() > messages_sent:
                        # send a sender abort
                        message = fragment_engine.create_sender_abort()
                        self.send_fragment(lora_socket, message)
                        print("## Error in the transmission of last window")
                        print("## EXIT sending process")
                        state = "ERROR"
                    elif not rec_c.uint:
                        # send a sender abort
                        message = fragment_engine.create_sender_abort()
                        self.send_fragment(lora_socket, message)
                        print("## Error MIC check of packet")
                        print("## EXIT sending process")
                        state = "ERROR"
                else:
                    if bmp.equals(rec_bmp):
                        new_bmp = Bitmap(profile.WINDOW_SIZE)
                        new_actual_window += 1
                        state = "RETRANSMISSION"
                    else:
                        new_bmp = rec_bmp
                        new_attempts += 1
                        state = "OK"
            else:
                print("## Error in ACK W header, expecting new ACK")
                state = "WAITING"

        return state, new_actual_window, new_bmp, new_attempts

    def _send_packet_always_ack(self, lora_socket):
        profile = self.id_profiles[self.actual_id]
        fragment_engine = FragmentEngine(profile, self.actual_id, self.actual_dtag)
        windows_number = self.compute_packet(self.actual_id, self.actual_dtag)
        print("Packet to sent: ", hexlify(self.packet.packet))
        print("Packet padding: ", hexlify(self.packet.packet_padding))
        actual_window = 0
        attempts = 0
        bmp = Bitmap(profile.WINDOW_SIZE)
        state = None
        self.msg_counter_sender = 0
        self.msg_counter_receiver = 0
        while actual_window < windows_number:
            if attempts > profile.MAX_ACK_REQUESTS:
                print("## Attempts number reach the limit of MAX_ACK_REQUESTS")
                print("## EXIT sending process")
                return
            # Send window
            messages_sent = self.send_window(lora_socket, actual_window, bmp)
            state = "WAITING"
            while state == "WAITING":
                state, actual_window, bmp, attempts = self._sender_receive_ack_always_process(lora_socket,
                                                                                              fragment_engine,
                                                                                              profile,
                                                                                              actual_window,
                                                                                              windows_number,
                                                                                              messages_sent,
                                                                                              attempts, bmp)
            if state == "ERROR":
                return
            elif state == "RETRANSMISSION" or state == "OK":
                pass
        print("## Packet sent")
        return

    def receive(self, mqtt_client, dev_id):
        print("")
        print("## Launching receive()")
        profile = self.id_profiles[self.actual_id]
        fragment_engine = FragmentEngine(profile, self.actual_id, self.actual_dtag)
        self.msg_counter_sender += 1
        if self.receiving_mode == FRCommon.FRModes.ALWAYS_ACK:
            message_type, headers = fragment_engine.receiver_message_recovery(self.receiving_buffer)
            print("## -> Message type: ", message_type)
            # Getting headers fields
            rec_rid_bits = headers[FRCommon.FRHeaders.R_ID].get_bits()
            rec_dtag_bits = headers[FRCommon.FRHeaders.D_TAG].get_bits()
            rec_w_bits = headers[FRCommon.FRHeaders.W].get_bits()
            rec_fcn_bits = headers[FRCommon.FRHeaders.FCN].get_bits()
            rec_mic = headers[FRCommon.FRHeaders.MIC]
            rec_payload = headers[FRCommon.FRHeaders.PAYLOAD]
            # Check Rule ID and DTag values
            if (rec_rid_bits.uint != self.actual_id) or (rec_dtag_bits.uint != self.actual_dtag):
                print("Rule ID or D Tag not expected")
                self.receiving_buffer = None
                return
            print("## -> Rule ID and DTag correct")
            print("## -> W={} ; FCN={}".format(rec_w_bits.uint, rec_fcn_bits.uint))
            # Check for messages types
            if message_type == FRCommon.FRMessages.SENDER_ABORT:
                print("## Received a SENDER-ABORT message")
                print("## EXIT receiving process")
                self.receiving_buffer = None
                self.stop_receiving()
                return
            elif message_type == FRCommon.FRMessages.ACK_REQUEST:
                print("## Received a ACK-REQUEST message")
                # message = fragment_engine.create_ack(self.actual_bitmap, self.actual_window).tobyte()
                # mqtt_client.send(dev_id, b2a_base64(message).decode('ascii'), port=1, sched="last")
                self.set_send_ack(True)
                self.msg_counter_receiver += 1
                self.receiving_buffer = None
                return
            else:
                print("## -> Receiving a Regular SCHC Fragment")
                # Check if W value is correct
                if (self.actual_window & FRCommon.lsb_mask[profile.w_size]) == rec_w_bits.uint:
                    print("## -> Correct window number")
                    if message_type == FRCommon.FRMessages.ALL1:
                        print("## -> Receiving All-1")
                        # ultimo fragmento de paquete
                        new_packet = self.packet
                        new_packet.add_window_to_packet(self.window)
                        new_packet.tiles.append(rec_payload)
                        new_packet.set_padding(0)
                        new_packet.construct_from_tiles(new_packet.tiles)
                        new_packet.calculate_mic(profile)
                        print("## -> Calculated MIC: ", new_packet.MIC)
                        if new_packet.MIC == rec_mic.get_bits().uint:
                            print("## -> MIC succesfully calculated, reassembling")
                            packet = new_packet
                            self.actual_bitmap.set_last_unsent()
                            self.ack_bitmap = self.actual_bitmap
                            self.set_send_ack(True)
                            self.msg_counter_receiver += 1
                            self.receiving_buffer = None
                            self.stop_receiving()
                            print("PACKET REASSEMBLED")
                            print("Packet: ", self.packet.packet.hex())
                            return
                        else:
                            print("## -> Window incomplete, expecting retransmission")
                            self.ack_bitmap = self.actual_bitmap
                            self.set_send_ack(True)
                            self.msg_counter_receiver += 1
                            self.receiving_buffer = None
                    # Check if fragment is the last fragment of a window that is not the last window
                    elif message_type == FRCommon.FRMessages.REGULAR and rec_fcn_bits.uint == 0:
                        print("## -> Receiving All-0")
                        self.actual_bitmap.set_bit_by_fcn(rec_fcn_bits.uint, True)
                        self.window[rec_fcn_bits.uint] = rec_payload
                        # Check if the window is complete
                        if self.actual_bitmap.get_missing_fragments() == 0:
                            self.ack_bitmap = self.actual_bitmap
                            self.set_send_ack(True)
                            self.msg_counter_receiver += 1
                            self.actual_window += 1
                            self.packet.add_window_to_packet(self.window)
                            self.reset_window()
                            self.receiving_buffer = None
                            print("## -> Window complete, expecting new window")
                            return

                        else:
                            print("## -> Window incomplete, expecting retransmission")
                            self.ack_bitmap = self.actual_bitmap
                            self.set_send_ack(True)
                            self.msg_counter_receiver += 1
                            self.receiving_buffer = None
                            return

                    else:
                        self.actual_bitmap.set_bit_by_fcn(rec_fcn_bits.uint, True)
                        self.window[rec_fcn_bits.uint] = rec_payload
                        print("## -> Saving fragment in window")
                else:
                    print("## -> Incorrect window value, ignoring fragment")
                self.receiving_buffer = None
        print("## Quitting receive()")
        print("")
        return

    def start_receiving(self, rule_id, d_tag):
        print("## Starting receiving a new SCHC packet")
        self.actual_id = rule_id
        self.actual_dtag = d_tag
        self.msg_counter_sender = 0
        self.msg_counter_receiver = 0
        profile = self.id_profiles[self.actual_id]
        self.actual_frag_engine = FragmentEngine(profile, self.actual_id, self.actual_dtag)
        self.receiving = True
        self.receiving_mode = profile.mode
        self.actual_window = 0
        self.receiving_buffer = None
        self.packet = Packet()
        self.reset_window()
        return

    def reset_window(self):
        profile = self.id_profiles[self.actual_id]
        self.window = [None] * profile.WINDOW_SIZE
        self.actual_bitmap = Bitmap(profile.WINDOW_SIZE)
        return

    def stop_receiving(self):
        self.receiving = False
        return

    def reassembly(self):
        all_tiles = self.packet.tiles
        self.packet.construct_from_tiles(all_tiles)
        return

    def set_send_ack(self, value):
        self.send_ack = value
