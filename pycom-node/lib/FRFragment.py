class FRFragment:
    
    def  __init__(self, header, payload, padding):
        self._header = header
        self._payload = payload
        self._padding = padding