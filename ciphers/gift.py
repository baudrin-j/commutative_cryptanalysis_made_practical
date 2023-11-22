from sage.crypto.sboxes import GIFT as S
from ciphers.cipher import AESLikeCipher
from ciphers.linearlayer import GIFT64, GIFT128, ff_matrix_to_binary
from sage.matrix.constructor import Matrix
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.combinat.permutation import Permutation


class Gift(AESLikeCipher):

    def __init__(self, n=64):
        if n not in [64, 128]:
            raise ValueError("n must be in [64, 128]")

        mc_binary_matrix = Matrix(GF(2), Permutation([
            1, 6, 11, 16,
            13, 2, 7, 12,
            9, 14, 3, 8,
            5, 10, 15, 4
        ]).to_matrix())

        if n == 64:
            sc_binary_matrix = ff_matrix_to_binary(Matrix(GF(2**4), Permutation([
                1 + (i//4) + ((i*4) % 16) for i in range(16)
            ]).to_matrix()))
            nbr_sboxes = 16
            nbr_superboxes = 4
        else:
            sc_binary_matrix = ff_matrix_to_binary(Matrix(GF(2**4), Permutation([
                1 + (i//4) + ((i*8) % 32) for i in range(32)
            ]).to_matrix()))
            nbr_sboxes = 32
            nbr_superboxes = 8

        super().__init__(S, mc_binary_matrix, sc_binary_matrix, nbr_sboxes, nbr_superboxes, f"GIFT-{n}")
        assert self.L == (GIFT64 if n == 64 else GIFT128).binary_matrix()
