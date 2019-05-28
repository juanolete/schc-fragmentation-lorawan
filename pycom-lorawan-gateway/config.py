""" LoPy LoRaWAN Nano Gateway configuration options """

import machine
import ubinascii

WIFI_MAC = ubinascii.hexlify(machine.unique_id()).upper()
# Set  the Gateway ID to be the first 3 bytes of MAC address + 'FFFE' + last 3 bytes of MAC address
GATEWAY_ID = WIFI_MAC[:6] + "FFFE" + WIFI_MAC[6:12]

#SERVER = 'router.brazil.thethings.network'
SERVER = 'router.eu.thethings.network'
#SERVER = 'router.us-west.thethings.network'
#SERVER = 'router.us.thethings.network'
PORT = 1700

NTP = "pool.ntp.org"
NTP_PERIOD_S = 3600


WIFI_SSID = 'Alumnos-DIE'
WIFI_PASS = '17alumnosdie17'

'''
WIFI_SSID = 'RENATA'
WIFI_PASS = '224597604'
'''
'''
WIFI_SSID = 'VTR-1973719'
WIFI_PASS = 't5hhQzpfjvxc'
'''
'''
WIFI_SSID = 'TelecoAv'
WIFI_PASS = 'pulp0azul'
'''

# for AU915
#LORA_FREQUENCY = 915020000
LORA_FREQUENCY = 916800000
LORA_GW_DR = "SF10BW125" # DR_0
LORA_NODE_DR = 3
