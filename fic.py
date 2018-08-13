import bitstring

class fic(object):
    def __init__(self, dp):
        self._dp = dp

    def _unpuncture(self, fic_punctured):
        fic_unpuctured = bitstring.BitArray()
        index = 0
        for bit in self._dp.assembled_fic_puncturing_sequence:
            if bit:
                fic_unpuctured.append('0b1' if fic_punctured[index] else '0b0')
                index+=1
            else:
                fic_unpuctured.append('0b0')
        return fic_unpuctured
