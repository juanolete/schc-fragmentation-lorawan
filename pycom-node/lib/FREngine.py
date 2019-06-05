from FRConstants import *
from FRPacket import FRPacket as Packet
from FRProfile import FRProfile as Profile
from FRRuleId import FRRuleID as RuleId
from FRFragment import FRFragment as Fragment
from FRWindow import FRWindow as Window


class FREngine:

    def __init__(self):
        self._rule_id = None
        self._profile = None
        self._packet = None
        self._fragments = None
        self._lora_params = None
        self._timers = None
        self._counters = None
        pass

    def initialize(self, rule_id, profile, lora_params):
        self._ruleId = rule_id
        self._profile = profile
        self._loraParams = lora_params
        return
    
    def set_profile(self, profile):
        self._profile = profile
        return
    
    def set_ruleId(self, ruleId):
        self._rule_id = ruleId
        return

    def set_packet(self, packet):
        self._packet = packet
        return

    def begin_fragmentation(self):
        self._get_fragments()
        self._get_windows()
        #self._set_timers()
        #self._set_counters()

        return
    
    def _get_fragments(self):
        headers = self._get_headers()
        self._fragments = headers + payloads

        return 