from sage.crypto.sboxes import CRAFT as S
from ciphers.cipher import AESLikeCipher
from sage.matrix.constructor import Matrix
from ciphers.linearlayer import ff_matrix_to_binary
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.combinat.permutation import Permutation

class Craft(AESLikeCipher):
    def __init__(self):
        MC = Matrix(GF(2**4), 4, 4, map(GF(2**4).fetch_int, [1, 0, 1, 1,
                                                             0, 1, 0, 1,
                                                             0, 0, 1, 0,
                                                             0, 0, 0, 1]))
        MC = ff_matrix_to_binary(MC)
        SC = Permutation([16, 11, 10, 5, 4, 7, 6, 9, 8, 3, 2, 13, 12, 15, 14, 1])
        SC = ff_matrix_to_binary(Matrix(GF(2**4), 16, 16,
                                        list(map(GF(2**4).fetch_int,
                                                 SC.to_matrix().list()))))
        super().__init__(S, MC, SC, 16, 4, "Craft")
