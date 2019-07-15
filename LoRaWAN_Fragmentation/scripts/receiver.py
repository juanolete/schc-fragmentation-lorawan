import ttn
import binascii
import time

# Fragmentation imports
from FREngine import FREngine
from FRCommon import *
from FRProfile import FRProfile
from binascii import b2a_base64

# TTN Connection
app_id = "lorawan-fragmentation"
dev_id = "new-pycom-0"
access_key = "ttn-account-v2.0-7mYfExeud7ndGjvMCJQXaoUZ5GWy4TFVuivyrczzs"
handler = ttn.HandlerClient(app_id, access_key)
mqtt_client = handler.data()
mqtt_client.connect()

# Fragmentation elements
# Create profiles
profile_0 = FRProfile()
profile_0.enable_fragmentation()
profile_0.select_fragmentation_mode(mode=FRModes.ALWAYS_ACK)

profile_1 = FRProfile()
profile_1.enable_fragmentation()
profile_1.select_fragmentation_mode(mode=FRModes.ACK_ON_ERROR)

profile_2 = FRProfile()
profile_2.enable_fragmentation()
profile_2.select_fragmentation_mode(mode=FRModes.NO_ACK)

fragmentation = FREngine()
fragmentation.add_profile(0, profile_0)
fragmentation.add_profile(1, profile_1)
fragmentation.add_profile(2, profile_2)


# Receiver function
def uplink_callback(msg, client, frag_engine=fragmentation):
    print("\n## -> Entering unplink_callback()")
    fragment = binascii.a2b_base64(msg.payload_raw)
    if fragment == DUMMY_MESSAGE:
        print("## -> Received DUMMY MSG")
        frag_engine.bits_counter_sender += len(fragment) * 8
    else:
        if not frag_engine.receiving:
            rid, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(3, fragment, len(fragment) * 8,
                                                                                             0, 8)
            rid_number = rid.get_bits().uint
            profile = frag_engine.id_profiles[rid_number]
            dtag, fragment_bits_left, octet_index, octet_bits_left = take_field_from_fragment(profile.dtag_size,
                                                                                              fragment,
                                                                                              fragment_bits_left,
                                                                                              octet_index,
                                                                                              octet_bits_left)
            dtag_number = dtag.get_bits().uint
            if dtag_number != frag_engine.actual_dtag:
                print("## Starting receiving packet")
                print("## New Rule ID: ", rid_number)
                print("## New DTag: ", dtag_number)
                frag_engine.start_receiving(rid_number, dtag_number)
            else:
                print("## Continue reciving packet")
                print("## New Rule ID: ", rid_number)
                print("## New DTag: ", dtag_number)
                frag_engine.continue_receiving()
        if frag_engine.receiving:
            frag_engine.bits_counter_sender += len(fragment) * 8
            print("## New fragment: ", fragment)
            frag_engine.receiving_buffer = fragment
            frag_engine.receive(mqtt_client, msg.dev_id)
            if frag_engine.send_ack:
                print("## -> Scheduling ACK with W={} and BMP={} for the next reception of DUMMY MESSAGE".format(
                    frag_engine.ack_window, frag_engine.ack_bitmap.bitmap))
                message = frag_engine.actual_frag_engine.create_ack(frag_engine.ack_bitmap,
                                                                    frag_engine.actual_c,
                                                                    frag_engine.ack_window)
                frag_engine.bits_counter_receiver += message.len
                print("## -> Receiver bits sent: ", frag_engine.bits_counter_receiver)
                print("ACK: ", message.hex)
                time.sleep(1)
                mqtt_client.send(dev_id, b2a_base64(message.tobytes()).decode('ascii'), port=1, sched="last")
                frag_engine.set_send_ack(False)


    print("## -> Exit uplink_callback()\n")
    return


mqtt_client.set_uplink_callback(uplink_callback)

while True:
    pass
