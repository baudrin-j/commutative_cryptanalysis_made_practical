from sage.crypto.sboxes import Rectangle as S
from ciphers.cipher import Cipher
from sage.combinat.permutation import Permutation
from sage.matrix.constructor import Matrix as matrix
from sage.rings.finite_rings.finite_field_constructor import GF
import itertools

class Rectangle(Cipher):

    def __init__(self):
        # Rectangle is bitsliced so linear layer is not only SR but also conversion
        # s.t. lsbs,...,msbs of sboxes are next to each other and again back s.t. all
        # bits of one sboxs are next to each other
        P = Permutation(map(lambda x: x+1,
                          list(itertools.chain(*[list(range(i, 64, 16)) for i in range(16)]))))
        P = matrix(GF(2), P.to_matrix())
        SR = Permutation(map(lambda x: x+1,
                          list(range(16)) +
                          [31] + list(range(16, 31)) +
                          list(range(36, 48)) + list(range(32, 36)) +
                          list(range(51, 64)) + list(range(48, 51))))
        SR = matrix(GF(2), SR.to_matrix())
        L = P.inverse() * SR * P
        super().__init__(S, L, 16, "RECTANGLE")
