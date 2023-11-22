from sage.crypto.sboxes import Scream as S
from ciphers.cipher import Cipher
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.matrix.constructor import Matrix
from sage.modules.free_module_element import vector
from sage.modules.free_module import VectorSpace

class Scream(Cipher):
    def __init__(self):        
        M_L =  [[0, 0, 1, 1, 1, 0, 1, 0, 0, 0, 0, 1, 1, 1, 0, 0],
                [1, 0, 0, 1, 0, 1, 0, 1, 0, 1, 0, 0, 1, 0, 1, 0],
                [1, 1, 0, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 0],
                [1, 0, 0, 0, 0, 0, 1, 1, 0, 1, 1, 0, 1, 0, 0, 1],
                [1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1],
                [0, 0, 0, 0, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 0],
                [0, 0, 1, 0, 0, 1, 0, 0, 1, 0, 1, 0, 0, 1, 1, 1],
                [1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 1],
                [1, 1, 0, 1, 0, 0, 1, 0, 0, 1, 1, 0, 0, 0, 1, 0],
                [1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1],
                [1, 1, 0, 0, 1, 1, 0, 0, 1, 0, 0, 0, 0, 1, 0, 1],
                [0, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0],
                [0, 1, 0, 0, 1, 0, 0, 0, 1, 1, 1, 0, 0, 1, 1, 0],
                [1, 1, 1, 1, 0, 1, 1, 0, 0, 1, 0, 1, 1, 1, 1, 0],
                [1, 1, 0, 1, 1, 0, 0, 0, 0, 0, 0, 0, 1, 1, 1, 0],
                [1, 0, 0, 0, 1, 1, 0, 1, 0, 1, 0, 1, 0, 0, 0, 1]]
        M_L = Matrix(GF(2), 16, 16, M_L)
        def build_L(state):
            # state vector -> array of rows
            x = [state[i::8] for i in range(8)]
            y = [M_L * xx for xx in x]
            state_ = vector(state.base_ring(), 128)
            for i in range(8):
                state_[i::8] = y[i]
            return state_
        L = Matrix(GF(2), 128, 128)
        for i, e in enumerate(VectorSpace(GF(2), 128).basis()):
            L[:, i] = build_L(e)
        super().__init__(S, L, 16, "Scream")
