from sage.crypto.sboxes import SKINNY_4 as S_4
from sage.crypto.sboxes import SKINNY_8 as S_8
from ciphers.cipher import AESLikeCipher
from ciphers.linearlayer import SKINNY_4 as SKINNY_4_L
from ciphers.linearlayer import SKINNY_8 as SKINNY_8_L
from ciphers.linearlayer import ff_matrix_to_binary


class Skinny(AESLikeCipher):

    def __init__(self, n=64):
        if n not in [64, 128]:
            raise ValueError("n must be in [64, 128]")
        elif n == 64:
            MC = ff_matrix_to_binary(SKINNY_4_L._mc)
            SC = ff_matrix_to_binary(SKINNY_4_L._sc)
            S = S_4
        else:
            MC = ff_matrix_to_binary(SKINNY_8_L._mc)
            SC = ff_matrix_to_binary(SKINNY_8_L._sc)
            S = S_8
        super().__init__(S, MC, SC, 16, 4, f"SKINNY-{n}", True)
