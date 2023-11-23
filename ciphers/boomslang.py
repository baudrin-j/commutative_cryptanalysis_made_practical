from sage.all import *
from sage.crypto.sbox import SBox
from sage.matrix.constructor import Matrix
from ciphers.linearlayer import ff_matrix_to_binary
from sage.combinat.permutation import Permutation
from ciphers.cipher import AESLikeCipher

S = SBox([8, 2, 4, 0xa, 5, 0xf, 7, 6, 0, 0xc, 0xb, 9, 0xe, 0xd, 1, 3])

class Boomslang(AESLikeCipher):
    def __init__(self):
        I  = Matrix(GF(2), 4, 4, [[1, 0, 0, 0],
                                  [0, 1, 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1]])
        X  = Matrix(GF(2), 4, 4, [[0, 1, 0, 0],
                                  [0, 0, 1, 0],
                                  [0, 0, 0, 1],
                                  [1, 0, 0, 0]])
        X2 = Matrix(GF(2), 4, 4, [[0, 0, 1, 0],
                                  [0, 0, 0, 1],
                                  [1, 0, 0, 0],
                                  [0, 1, 0, 0]])
        MC = block_matrix(GF(2), 4, 4, [[ 0,  I,  X, X2],
                                        [X2,  0,  I,  X],
                                        [ X, X2,  0,  I],
                                        [ I,  X, X2,  0]])
        SC = Permutation([1, 30, 27, 24, 5, 2, 31, 28, 9, 6, 3, 32, 13, 10, 7,
                          4, 17, 14, 11, 8, 21, 18, 15, 12, 25, 22, 19, 16, 29,
                          26, 23, 20])
        SC = ff_matrix_to_binary(Matrix(GF(2**4), 32, 32,
                                        list(map(GF(2**4).fetch_int,
                                                 SC.to_matrix().list()))))
        super().__init__(S, mc_binary_matrix=MC, sc_binary_matrix=SC,
                         nbr_sboxes=32, nbr_superboxes=8, name="Boomslang")

