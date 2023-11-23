# LED uses PRESENT sbox
from sage.crypto.sboxes import PRESENT as S
from ciphers.cipher import AESLikeCipher
from ciphers.linearlayer import ff_matrix_to_binary
from ciphers.linearlayer import Left_ShiftRows
from sage.matrix.constructor import Matrix
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.rings.polynomial.polynomial_ring_constructor import PolynomialRing


class LED(AESLikeCipher):

    def __init__(self):
        P = PolynomialRing(GF(2), name="a")("a^4 + a + 1")
        F = GF(2**4, name="x", modulus=P, repr="int")
        MC = Matrix(F, 4, 4, map(F.fetch_int, [0x4, 0x1, 0x2, 0x2,
                                               0x8, 0x6, 0x5, 0x6,
                                               0xB, 0xE, 0xA, 0x9,
                                               0x2, 0x2, 0xF, 0xB,]))
        MC = ff_matrix_to_binary(MC)
        SC = Left_ShiftRows
        SC = ff_matrix_to_binary(Matrix(F, 16, 16, list(map(F.fetch_int,
                                                            SC.to_matrix().list()))))
        super().__init__(S, MC, SC, 16, 4, "LED")
