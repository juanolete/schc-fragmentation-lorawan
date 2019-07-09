import ttn
import binascii
import time
import FREngine
import FRProfile as profile


# TTN Connection
app_id = "lorawan-fragmentation"
dev_id = "new-pycom-0"
access_key = "ttn-account-v2.0-7mYfExeud7ndGjvMCJQXaoUZ5GWy4TFVuivyrczzs"
handler = ttn.HandlerClient(app_id, access_key)
mqtt_client = handler.data()
mqtt_client.connect()

# Fragmentation elements




# Receiver function
def uplink_callback(msg, client):
    data = bytes([1, 2, 3, 4])
    time.sleep(1)
    mqtt_client.send(dev_id, binascii.b2a_base64(data).decode('ascii'), port=1, sched="last")
    # mqtt_client.send(dev_id, "AQIDBA==", port=1, sched="replace")
    print("Receiverd uplink from ", msg.dev_id)
    data_bytes = binascii.a2b_base64(msg.payload_raw)
    print("Payload Bytes: ", data_bytes)
    print("Payload Hex: ", binascii.hexlify(data_bytes))



mqtt_client.set_uplink_callback(uplink_callback)


while True:
    pass
