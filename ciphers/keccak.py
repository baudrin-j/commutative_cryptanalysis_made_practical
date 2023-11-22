from sage.crypto.sbox import SBox
from ciphers.cipher import Cipher
from sage.matrix.constructor import Matrix
from sage.rings.finite_rings.finite_field_constructor import GF
from sage.modules.free_module_element import vector
from sage.modules.free_module import VectorSpace
from sage.rings.integer_ring import ZZ

S = []
for x in range(2**5):
    x0 = (x >> 0) & 1
    x1 = (x >> 1) & 1
    x2 = (x >> 2) & 1
    x3 = (x >> 3) & 1
    x4 = (x >> 4) & 1
    y0 = x0 ^((~x1) & x2)
    y1 = x1 ^((~x2) & x3)
    y2 = x2 ^((~x3) & x4)
    y3 = x3 ^((~x4) & x0)
    y4 = x4 ^((~x0) & x1)
    y = y0 + 2*y1 + 4*y2 + 8*y3 + 16*y4
    S.append(y)
S = SBox(S)

class Keccak(Cipher):

    def __init__(self, b=1600):
        self._b = b
        if self._b not in [25,50,100,200,400,800,1600]:
            raise ValueError("b must be in [25,50,100,200,400,800,1600]")
        self._w = b // 25

        def ROL(a, n, w):
            return ((a >> (w-(n%w))) + (a << (n%w))) % (1 << w)

        def build_L(state):
            w = self._w

            # state vector -> array of ints (each element corresponds to one sbox)
            X = [ZZ(list(state[5*i:5*(i+1)]), 2) for i in range(self._b // 5)]

            # array of sboxes -> array of lanes
            planes = [X[i::5] for i in range(5)]
            lanes = [[0 for _ in range(5)] for _ in range(5)]
            for y in range(5):
                for x in range(5):
                    lanes[x][y] = sum([((p >> x) & 1) << z for z, p in enumerate(planes[y])])

            # from: https://github.com/XKCP/XKCP/blob/master/Standalone/CompactFIPS202/Python/CompactFIPS202.py
            # Theta
            C = [lanes[x][0] ^ lanes[x][1] ^ lanes[x][2] ^ lanes[x][3] ^ lanes[x][4] for x in range(5)]
            D = [C[(x+4)%5] ^ ROL(C[(x+1)%5], 1, w) for x in range(5)]
            lanes = [[lanes[x][y]^D[x] for y in range(5)] for x in range(5)]
            # rho and pi
            (x, y) = (1, 0)
            current = lanes[x][y]
            for t in range(24):
                (x, y) = (y, (2*x+3*y)%5)
                (current, lanes[x][y]) = (lanes[x][y], ROL(current, (t+1)*(t+2)//2, w))

            # transpose state back
            X = []
            for z in range(w):
                for y in range(5):
                    x0 = (lanes[0][y] >> z) & 1
                    x1 = (lanes[1][y] >> z) & 1
                    x2 = (lanes[2][y] >> z) & 1
                    x3 = (lanes[3][y] >> z) & 1
                    x4 = (lanes[4][y] >> z) & 1
                    x = x0 + 2*x1 + 4*x2 + 8*x3 + 16*x4
                    X.append(x)
            state_ = vector(state.base_ring(), self._b)
            for i in range(self._b // 5):
                state_[5*i:5*(i+1)] = ZZ(X[i]).digits(2, padto=5)
            return state_
        L = Matrix(GF(2), self._b, self._b)
        for i, e in enumerate(VectorSpace(GF(2), self._b).basis()):
            L[:, i] = build_L(e)
        super().__init__(S, L, 5*self._w, f"Keccak[{b}]")
