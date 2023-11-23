from sage.crypto.sboxes import Midori_Sb0 as S
from ciphers.cipher import AESLikeCipher
from ciphers.linearlayer import Midori as Midori_L
from ciphers.linearlayer import ff_matrix_to_binary


class Midori(AESLikeCipher):

    def __init__(self):
        MC = ff_matrix_to_binary(Midori_L._mc)
        SC = ff_matrix_to_binary(Midori_L._sc)
        super().__init__(S, MC, SC, 16, 4, "Midori64")
