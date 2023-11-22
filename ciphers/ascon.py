from sage.crypto.sboxes import Ascon as S
from sage.matrix.constructor import Matrix
from sage.modules.free_module_element import vector
from sage.modules.free_module import VectorSpace
from sage.rings.finite_rings.finite_field_constructor import GF

from ciphers.cipher import Cipher
class Ascon(Cipher):

    def __init__(self):
        # build matrix for linear layer
        M_ROR = [(19*[0] + [1] + (64-19-1)*[0],
                  28*[0] + [1] + (64-28-1)*[0]),
                 (61*[0] + [1] + (64-61-1)*[0],
                  39*[0] + [1] + (64-39-1)*[0]),
                 ( 1*[0] + [1] + (64- 1-1)*[0],
                   6*[0] + [1] + (64- 6-1)*[0]),
                 (10*[0] + [1] + (64-10-1)*[0],
                  17*[0] + [1] + (64-17-1)*[0]),
                 ( 7*[0] + [1] + (64- 7-1)*[0],
                   41*[0] + [1] + (64-41-1)*[0])]
        M_ROR = list(map(lambda x: (Matrix.circulant(vector(GF(2), x[0])),
                                    Matrix.circulant(vector(GF(2), x[1]))), M_ROR))
        def build_L(state):
            # state vector -> array of rows
            x = [state[i::5] for i in range(5)]
            # apply linear layer
            x[0] += M_ROR[0][0] * x[0] + M_ROR[0][1] * x[0]
            x[1] += M_ROR[1][0] * x[1] + M_ROR[1][1] * x[1]
            x[2] += M_ROR[2][0] * x[2] + M_ROR[2][1] * x[2]
            x[3] += M_ROR[3][0] * x[3] + M_ROR[3][1] * x[3]
            x[4] += M_ROR[4][0] * x[4] + M_ROR[4][1] * x[4]
            # transform back
            state_ = vector(state.base_ring(), 320)
            for i in range(5):
                state_[i::5] = x[i]
            return state_
        L = Matrix(GF(2), 320, 320)
        for i, e in enumerate(VectorSpace(GF(2), 320).basis()):
            L[:, i] = build_L(e)
        super().__init__(S, L, 64, "Ascon")



