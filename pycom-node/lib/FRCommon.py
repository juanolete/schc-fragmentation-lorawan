from FRTile import FRTile as Tile

lsb_mask = [0b0, 0b00000001, 0b00000011, 0b00000111, 0b00001111, 0b00011111, 0b00111111, 0b01111111, 0b11111111]
DR_AUS915 = {
    # Mapping DR value with real Payload size in bytes
    # The application need 13 bytes so it has to be subtracted to the
    0: 51,
    1: 51,
    2: 51,
    3: 115,
    4: 222,
    5: 222,
    6: 222,
    8: 33,
    9: 109,
    10: 222,
    11: 222,
    12: 222,
    13: 222,
}


def padding_bits(actual_len, l2_word_size):
    return (l2_word_size - actual_len%l2_word_size)%l2_word_size


def bytes_to_int(byte):
    result = 0
    for b in byte:
        result = result * 256 + int(b)
    return result


def take_field_from_fragment(field_size: int, fragment: bytes,
                             in_fragment_bits_left: int, in_octet_index: int,
                             in_octet_bits_left: int):
    field = Tile(field_size)
    fragment_bits_left = in_fragment_bits_left
    octet_index = in_octet_index
    octet_bits_left = in_octet_bits_left
    while field.emptyBits > 0 and fragment_bits_left > 0:
        if field.emptyBits >= 8:
            if octet_bits_left == 8:
                field.add_byte(fragment[octet_index], octet_bits_left)
            else:
                aux_byte = fragment[octet_index] & lsb_mask[octet_bits_left]
                field.add_byte(aux_byte, octet_bits_left)
            fragment_bits_left -= octet_bits_left
            octet_bits_left = 8
            octet_index += 1
        else:
            if octet_bits_left > field.emptyBits:
                taken_bits = field.emptyBits
                aux_byte = (fragment[octet_index] << (8 - octet_bits_left)) & lsb_mask[8]
                aux_byte = aux_byte >> (8 - octet_bits_left)
                aux_byte = aux_byte >> (octet_bits_left - taken_bits)
                field.add_byte(aux_byte, taken_bits)
                fragment_bits_left -= taken_bits
                octet_bits_left -= taken_bits
            else:
                aux_byte = fragment[octet_index] & lsb_mask[octet_bits_left]
                field.add_byte(aux_byte, octet_bits_left)
                fragment_bits_left -= octet_bits_left
                octet_bits_left = 8
                octet_index += 1
    new_octet_index = octet_index
    new_fragment_bits_left = fragment_bits_left
    new_octet_bits_left = octet_bits_left
    return field, new_fragment_bits_left, new_octet_index, new_octet_bits_left

class FRModes:
    NO_ACK = 'NO_ACK'
    ALWAYS_ACK = 'ALWAYS_ACK'
    ACK_ON_ERROR = 'ACK_ON_ERROR'


class FRMessages:
    REGULAR = 'REGULAR'
    ALL1 = 'ALL-1'
    ACK = 'ACK'
    ACK_REQUEST = 'ACK-REQUEST'
    SENDER_ABORT = 'SENDER-ABORT'
    RECEIVER_ABORT = 'RECEIVER-ABORT'
