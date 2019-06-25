lsb_mask = [0b0, 0b00000001, 0b00000011, 0b00000111, 0b00001111, 0b00011111, 0b00111111, 0b01111111, 0b11111111]
DR_AUS915 = {
    # Mapping DR value with real Payload size in bytes
    # The application need 13 bytes so it has to be subtracted to the
    0: 19-13,
    1: 61-13,
    2: 133-13,
    3: 250-13,
    4: 250-13,
    8: 41-13,
    9: 117-13,
    10: 230-13,
    11: 230-13,
    12: 230-13,
    13: 230-13,
}


def padding_bits(actual_len, l2_word_size):
    return (l2_word_size - actual_len%l2_word_size)%l2_word_size


def bytes_to_int(byte):
    result = 0
    for b in byte:
        result = result * 256 + int(b)
    return result


class FRConstants:
    NO_ACK = 'NO_ACK'
    ALWAYS_ACK = 'ALWAYS_ACK'
    ACK_ON_ERROR = 'ACK_ON_ERROR'

