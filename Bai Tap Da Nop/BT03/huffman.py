# Nguồn code: https://github.com/reinhrst/pygreypeg

#from . import constants
import constants


class Huffman(object):
    def __init__(self):
        self._dc = 0
        self._buf = bytearray()
        self._bits = 0
        self._nbits = 0

    def write_bits(self, bits, nbits):
        mask = (1 << nbits) - 1
        self._bits <<= nbits
        self._bits |= bits & mask
        self._nbits += nbits
        while self._nbits >= 8:
            val = self._bits >> (self._nbits - 8)
            assert val < 256 and val >= 0, \
                "value = %x (%x, %d)" % (val, self._bits, self._nbits)
            self._buf.append(val)
            if val == 0xFF:
                # special rule because 0xFF is special
                self._buf.append(0)
            self._nbits -= 8
            mask = (1 << self._nbits) - 1
            self._bits &= mask

    @staticmethod
    def position_of_highest_1bit(value):
        count = 0
        while value:
            count += 1
            value >>= 1
        return count

    def encode_block(self, zz, length):
        if length > 0:
            val = zz[0] - self._dc
            self._dc = zz[0]
        else:
            val = -self._dc
            self._dc = 0

        bits = val
        if val < 0:
            val = -val
            bits = ~val
        nbits = Huffman.position_of_highest_1bit(val)
        self.write_bits(constants.dc_code[nbits], constants.dc_len[nbits])
        if nbits:
            self.write_bits(bits, nbits)

        # AC coefficients encoding (w/ RLE of zeroes)
        nz = 0
        for i in range(1, length):
            val = zz[i]
            if val == 0:
                nz += 1
            else:
                while nz >= 16:
                    # ZRL code
                    self.write_bits(
                        constants.ac_code[0xF0], constants.ac_len[0xF0])
                    nz -= 16
                bits = val
                if val < 0:
                    val = -val
                    bits = ~val
                nbits = Huffman.position_of_highest_1bit(val)
                j = (nz << 4) + nbits
                self.write_bits(constants.ac_code[j], constants.ac_len[j])
                if nbits:
                    self.write_bits(bits, nbits)
                nz = 0
        if length < 64:
            # EOB marker
            self.write_bits(constants.ac_code[0x00], constants.ac_len[0x00])

    def end_and_get_buffer(self):
        # flush any remaining junk
        self.write_bits(0x7F, 7)
        return self._buf
