import hashlib
from sys import argv
from math import floor, log2


def main(argv):
    input_integer_filename = argv[0]
    f = open(input_integer_filename, 'r')
    nums = f.readlines()
    nums = [int(i) for i in nums]
    result = solve(nums)
    print('l ' + str(result[0]))
    print('L')
    for content in result[1]:
        print(pb(content))
    print('U')
    for content in result[2]:
        print(pb(content))
    print(result[3])


def pb(b):
    return bin(b)[2:].zfill(8)


def solve(input_integers):
    m = max(input_integers)
    n = len(input_integers)

    el = floor(log2(m / n))

    L = create_l_bitarray(input_integers, el)
    U = create_u_bitarray(input_integers, el, n)

    m = hashlib.sha256()
    m.update(L)
    m.update(U)

    digest = m.hexdigest()

    return el, L, U, digest


# if we want to get 4 last digits of a byte
# e.g. 01010101
# we must use a mask and the AND operation to get them
# 01010101 AND 00001111 -> 00000101
def create_mask_last_digits(n):
    result = 1
    for i in range(0, n - 1):
        result = (result << 1) | 1

    return result


# if we want to get 4 first digits of a byte
# e.g. 01010101
# we must use a mask and the AND operation to get them
# 01010101 AND 11110000 -> 01010000
#
# since we already can compute the mask for the last digits it is enough
# to use the XOR operation to compute the mask for the first digits
# e.g. 00001111 XOR 11111111 -> 11110000
def create_mask_first_digits(n):
    return create_mask_last_digits(n) ^ 255


def create_l_bitarray(input_bin, el):
    result = bytearray()

    # we need to track how many bits remain in the current byte so we know when
    # to insert it to the bytearray
    current_byte = 0
    remaining_bits_on_current_byte = 8

    mask = create_mask_last_digits(el)

    for b in input_bin:
        for i in reversed(range(0, el)):
            if remaining_bits_on_current_byte == 0:
                result.append(current_byte)
                current_byte = 0
                remaining_bits_on_current_byte = 8
            # make space for the next bit -> (current_byte << 1)
            # select last el bits of the number -> (b & mask) >> i
            # select only last bit-> & 1
            current_byte = (current_byte << 1) | (((b & mask) >> i) & 1)
            remaining_bits_on_current_byte = remaining_bits_on_current_byte - 1

    # left shift current byte in order for it to fill with zeros if there are bits remaining
    if remaining_bits_on_current_byte > 0:
        current_byte = current_byte << remaining_bits_on_current_byte

    # if there are any leftover bits on the current byte variable add it to the bytearray
    if current_byte > 0:
        result.append(current_byte)

    return result


def create_u_bitarray(input_ints, el, n):
    result = bytearray()
    mask = create_mask_first_digits(el)

    input_ints_before_retraction = []
    for i in range(0, n):

        # select first 8 - el digits
        d = (input_ints[i] & mask) >> el
        # note the integer in order to compute subtraction later
        input_ints_before_retraction.append(d)

        # if i is 0, no operation is needed
        if i > 0:
            d = d - input_ints_before_retraction[i - 1]
            if d < 0:
                # don't know why this works
                d = d + (2 ** (8 - el))

        # input is not needed any more, so in order to save some runtime space we overwrite it
        input_ints[i] = d

    current_byte = 0
    bits_remaining = 8

    for input_integer in input_ints:
        for i in (range(0, input_integer)):
            if bits_remaining == 0:
                result.append(current_byte)
                current_byte = 0
                bits_remaining = 8

            # Create zeros i times in the end of the byte
            current_byte = (current_byte << 1)
            bits_remaining = bits_remaining - 1

        if bits_remaining == 0:
            result.append(current_byte)
            current_byte = 0
            bits_remaining = 8

        # After we filled with zeros write 1 to the end of the byte to mark the start of the next number
        current_byte = (current_byte << 1) | 1
        bits_remaining = bits_remaining - 1

    if bits_remaining > 0:
        current_byte = current_byte << bits_remaining
    if current_byte > 0:
        result.append(current_byte)

    return result


if __name__ == "__main__":
    main(argv[1:])
