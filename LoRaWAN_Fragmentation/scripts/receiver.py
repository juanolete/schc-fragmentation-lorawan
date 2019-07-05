import base64
import ttn
import binascii

app_id = "lorawan-fragmentation"
dev_id = "new-pycom-0"
access_key = "ttn-account-v2.0-7mYfExeud7ndGjvMCJQXaoUZ5GWy4TFVuivyrczzs"
handler = ttn.HandlerClient(app_id, access_key)
mqtt_client = handler.data()
mqtt_client.connect()

def uplink_callback(msg, client):
    mqtt_client.send(dev_id, "AQIDBA==", port=1, sched="replace")
    print("Receiverd uplink from ", msg.dev_id)
    data_bytes = base64.b64decode(msg.payload_raw)
    print("Payload Bytes: ", data_bytes)
    print("Payload Hex: ", binascii.hexlify(data_bytes))
    downlink = bytes([1,2,3,4])
    # mqtt_client.send(msg.dev_id, "AQIDBA==", port=1)


mqtt_client.set_uplink_callback(uplink_callback)


while True:
    pass
