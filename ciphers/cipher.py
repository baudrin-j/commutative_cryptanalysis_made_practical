from abc import ABC, abstractmethod
from sage.matrix.special import block_diagonal_matrix
from sage.modules.free_module_element import vector
from sage.crypto.sbox import SBox
from sage.rings.integer_ring import ZZ


class Cipher(ABC):
    # basic SPN cipher (without key and constant addition)

    def __init__(self, S, L, nbr_sboxes, name):
        self.S = S
        self.S_inverse = S.inverse()
        # make sure that bit order is not messed up
        S_hat = SBox([ZZ((S(ZZ(x).digits(2, padto=len(S)))), 2) for x in range(2**len(S))])
        self.S_ = [S_hat.component_function(1 << i).algebraic_normal_form() for i in range(len(S))]
        self.S_inverse_ = [S_hat.inverse().component_function(1 << i).algebraic_normal_form()
                           for i in range(len(S))]
        self.nbr_sboxes = nbr_sboxes
        self.L = L
        self.L_inverse = L.inverse()
        self.name = name

    def __repr__(self):
        return self.name

    def inverse(self):
        return Cipher(self.S_inverse, self.L_inverse, self.nbr_sboxes, self.name + " (inverse)")

    def sbox_layer(self, state, nbr_sboxes=None):
        # slow but allows evaluation of polynomials
        if nbr_sboxes is None:
            nbr_sboxes = self.nbr_sboxes
        s_ = vector(state.base_ring(), len(state))
        b = len(self.S)
        for j in range(nbr_sboxes): # iterate sboxes
            x = state[b*j:b*(j+1)]
            for i in range(b): # iterate output bits of sboxs
                s_[b*j+i] = self.S_[i](*x)
        return s_

    def sbox_layer_inverse(self, state, nbr_sboxes=None):
        if nbr_sboxes is None:
            nbr_sboxes = self.nbr_sboxes
        s_ = vector(state.base_ring(), len(state))
        b = len(self.S)
        for j in range(nbr_sboxes): # iterate sboxes
            x = state[b*j:b*(j+1)]
            for i in range(b): # iterate output bits of sboxs
                s_[b*j+i] = self.S_inverse_[i](*x)
        return s_

    def sbox_layer_faster(self, state, nbr_sboxes=None):
        # a bit faster but only GF(2)
        if nbr_sboxes is None:
            nbr_sboxes = self.nbr_sboxes
        s_ = vector(state.base_ring(), len(state))
        b = len(self.S)
        for j in range(nbr_sboxes): # iterate sboxes
            s_[b*j:b*(j+1)] = self.S(state[b*j:b*(j+1)])
        return s_

    def sbox_layer_inverse_faster(self, state, nbr_sboxes=None):
        # a bit faster but only GF(2)
        if nbr_sboxes is None:
            nbr_sboxes = self.nbr_sboxes
        s_ = vector(state.base_ring(), len(state))
        b = len(self.S)
        for j in range(nbr_sboxes): # iterate sboxes
            s_[b*j:b*(j+1)] = self.S_inverse(state[b*j:b*(j+1)])
        return s_


    def linear_layer(self, state):
        return self.L*state

    def linear_layer_inverse(self, state):
        return self.L_inverse*state

class AESLikeCipher(Cipher):

    def __init__(self, S, mc_binary_matrix, sc_binary_matrix, nbr_sboxes, nbr_superboxes, name, sc_first=False):
        self.nbr_superboxes = nbr_superboxes
        self.mc_binary_matrix = mc_binary_matrix # only one superbox
        self.mc_inverse_binary_matrix = mc_binary_matrix.inverse()
        self.mc_layer_binary_matrix = block_diagonal_matrix(*[mc_binary_matrix for _ in range(nbr_superboxes)])
        self.mc_layer_binary_matrix_inverse = self.mc_layer_binary_matrix.inverse()
        self.sc_binary_matrix = sc_binary_matrix
        self.sc_inverse_binary_matrix = sc_binary_matrix.inverse()
        self.sc_first = sc_first
        L = self.mc_layer_binary_matrix*self.sc_binary_matrix if sc_first \
            else self.sc_binary_matrix*self.mc_layer_binary_matrix
        super().__init__(S, L, nbr_sboxes, name)

    def inverse(self):
        return AESLikeCipher(
            self.S_inverse, self.mc_inverse_binary_matrix, self.sc_inverse_binary_matrix,
            self.nbr_sboxes, self.nbr_superboxes, self.name + " (inverse)", not self.sc_first
        )

    def superbox(self, state):
        nbr_sboxes_per_superbox = self.nbr_sboxes // self.nbr_superboxes
        state = self.sbox_layer(state, nbr_sboxes=nbr_sboxes_per_superbox)
        state = self.mc_binary_matrix * state
        state = self.sbox_layer(state, nbr_sboxes=nbr_sboxes_per_superbox)
        return state

    def mc(self, state):
        return self.mc_layer_binary_matrix * state
    def mc_inverse(self, state):
        return self.mc_layer_binary_matrix_inverse * state
    def sc(self, state):
        return self.sc_binary_matrix * state
    def sc_inverse(self, state):
        return self.sc_inverse_binary_matrix * state

