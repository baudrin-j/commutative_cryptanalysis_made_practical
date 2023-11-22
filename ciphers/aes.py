from sage.crypto.sboxes import AES as S
from ciphers.cipher import AESLikeCipher
from ciphers.linearlayer import AES as L
from ciphers.linearlayer import ff_matrix_to_binary



class AES(AESLikeCipher):

    def __init__(self):
        MC = ff_matrix_to_binary(L._mc)
        SR = ff_matrix_to_binary(L._sc)
        super().__init__(S, MC, SR, 16, 4, "AES")

