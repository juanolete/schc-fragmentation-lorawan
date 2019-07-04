import time
import ttn

app_id = "lorawan-fragmentation"
access_key = "ttn-account-v2.0-7mYfExeud7ndGjvMCJQXaoUZ5GWy4TFVuivyrczzs"

def uplink_callback(msg, client):
    print("Receiverd uplink from ", msg.dev_id)
    print(msg)

handler = ttn.HandlerClient(app_id, access_key)

mqtt_client = handler.data()
mqtt_client.set_uplink_callback(uplink_callback)
mqtt_client.connect()

while True:
    pass
