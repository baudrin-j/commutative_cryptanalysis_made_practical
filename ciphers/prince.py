from sage.crypto.sboxes import PRINCE as S
from ciphers.cipher import AESLikeCipher
from sage.all import *
from sage.matrix.constructor import Matrix as matrix
from sage.matrix.special import block_diagonal_matrix
from sage.rings.finite_rings.finite_field_constructor import GF
from ciphers.linearlayer import ff_matrix_to_binary
from ciphers.linearlayer import Left_ShiftRows

class Prince(AESLikeCipher):

    def __init__(self, use_M0_HAT=True):
        M0 = matrix(GF(2), 4, 4, [0, 0, 0, 0,
                                  0, 1, 0, 0,
                                  0, 0, 1, 0,
                                  0, 0, 0, 1])
        M1 = matrix(GF(2), 4, 4, [1, 0, 0, 0,
                                  0, 0, 0, 0,
                                  0, 0, 1, 0,
                                  0, 0, 0, 1])
        M2 = matrix(GF(2), 4, 4, [1, 0, 0, 0,
                                  0, 1, 0, 0,
                                  0, 0, 0, 0,
                                  0, 0, 0, 1])
        M3 = matrix(GF(2), 4, 4, [1, 0, 0, 0,
                                  0, 1, 0, 0,
                                  0, 0, 1, 0,
                                  0, 0, 0, 0])
        M0_HAT = block_matrix(GF(2), 4, 4, [M0, M1, M2, M3,
                                            M1, M2, M3, M0,
                                            M2, M3, M0, M1,
                                            M3, M0, M1, M2])
        M1_HAT = block_matrix(GF(2), 4, 4, [M1, M2, M3, M0,
                                            M2, M3, M0, M1,
                                            M3, M0, M1, M2,
                                            M0, M1, M2, M3])
        M_ = block_diagonal_matrix([M0_HAT, M1_HAT, M1_HAT, M0_HAT])
        SR = Left_ShiftRows
        SR = ff_matrix_to_binary(Matrix(GF(2**4), 16, 16,
                                        list(map(GF(2**4).fetch_int,
                                                 SR.to_matrix().list()))))
        if use_M0_HAT:
            super().__init__(S, M0_HAT, SR, 16, 4, "Prince")
        else:
            super().__init__(S, M1_HAT, SR, 16, 4, "Prince")
        # Prince has two different MC matrices so manual adjustement is needed
        self.mc_layer_binary_matrix = M_
        self.mc_layer_binary_matrix_inverse = M_.inverse()
