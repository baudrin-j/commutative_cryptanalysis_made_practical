# COMMUTATIVE CRYPTANALYSIS MADE PRACTICAL
# This file contains verifications for the content of Appendix A:
# Connexions between Commutative Cryptanalysis and Conjugation
# (Note that variables are indexed starting from 0 here, but starting from 1 in the paper)

from sboxU import *  # Available at https://github.com/lpp-crypto/sboxU

#region MIDORI CONSTANTS
# Midori Sbox
SB0 = [0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6]

# Midori MC
def midori_MC():
    """ Return the LUT of the 16-bit mapping corresponding to Midori MixColumn. """
    mc = []
    for i in range(2 ** 16):
        i = hex(i)[2:].zfill(4)  # i as hex string of size 4
        i0 = int(i[1], 16) ^ int(i[2], 16) ^ int(i[3], 16)
        i1 = int(i[2], 16) ^ int(i[3], 16) ^ int(i[0], 16)
        i2 = int(i[3], 16) ^ int(i[0], 16) ^ int(i[1], 16)
        i3 = int(i[0], 16) ^ int(i[1], 16) ^ int(i[2], 16)
        mc.append(i0 * (16 ** 3) + i1 * (16 ** 2) + i2 * (16 ** 1) + i3 * (16 ** 0))
    return mc
MC = midori_MC()
#endregion

#region Print utils
BLUE = '\033[94m'
ENDCOLOR = '\033[0m'
def print_anf(lut, label=""):
    anf = algebraic_normal_form(lut)
    if label:
        print('-'*10, label, '-'*10)
    for i, x in enumerate(anf):
        if i == 0:
            print(BLUE + "LSB\t\t" + ENDCOLOR, end="")
        elif i == len(anf) - 1:
            print(BLUE + "MSB\t\t" + ENDCOLOR, end="")
        else:
            print(" " * 8, end="")
        print("y" + str(i)+ " = " + str(x))
    print()
#endregion

#region Composition and inverse utils
def xor_lut(lut_a, lut_b):
    """ Return the LUT of f XOR g given the LUT of f and g."""
    return [x ^ y for (x, y) in zip(lut_a, lut_b)]

def comp3(lut1, lut2, lut3):
    """ Return the LUT of the composition of 3 functions given as LUT."""
    return [lut1[lut2[lut3[x]]] for x in range(len(lut3))]


def comp2(lut1, lut2):
    """ Return the LUT of the composition of 2 functions given as LUT."""
    return [lut1[lut2[x]] for x in range(len(lut2))]


def in_parallel_4_4(s):
    """Return the LUT of the 16-bit mapping corresponding to 4 sbox s in parallel.
    """
    parallel_sboxes = []
    m = int("0xf", 16)
    for i in range(2**16):
        t = 0
        for j in range(4):
            t |= (s[(i >> (4 * j)) & m] << (4 * j))
        parallel_sboxes.append(t)
    return parallel_sboxes


def inverse_parallel(lut):
    """Return, in this order, the LUT of :
        - the inverse of p
        - 4-time parallel p
        - 4-time parallel p^{-1}
    """
    lut_i = inverse(lut)
    parallel = in_parallel_4_4(lut)
    parallel_i = inverse(parallel)
    return lut_i, parallel, parallel_i
#endregion

#region Study utils
def anf_conjugate_ark(g):
    """ Return the ANF of the conjugated add round constant layer"""
    gi = inverse(g)
    gi_xor_key = dict()
    for i, x in enumerate(algebraic_normal_form(gi)):
        gi_xor_key[poly_ring('x%d' % i)] = poly_ring(x) + poly_ring('k%d' % i)
    res = []
    for i in range(n):
        res.append(algebraic_normal_form(g)[i].subs(gi_xor_key))
    return res


def is_proba_z_differential(a, lut, z):
    """ Return the list of b such that a -> b with probability z/len(lut) through f (given as LUT). """
    return [(a, i) for i, v in enumerate(ddt_row(lut, a)) if v == z]


def differential_study(g, tested_diffs):
    gi, G, Gi = inverse_parallel(g)
    g_sb0_gi = comp3(g, SB0, gi)
    studied_functions = [g_sb0_gi, comp3(G, MC, Gi)]

    for f, diff in zip(studied_functions, tested_diffs):
        assert is_proba_z_differential(diff, f, len(f)) == [(diff, diff)]
#endregion


if __name__ == '__main__':
    ##################################################
    # A.3.3 Probability-1 DIFF TRAIL FOR CONJUGATES #
    ##################################################
    G_g = [0, 1, 3, 2, 4, 5, 7, 6, 8, 9, 10, 11, 12, 13, 14, 15]
    print_anf(G_g, 'ANF G_g')

    L_a = [0, 5, 1, 4, 2, 7, 3, 6, 8, 13, 9, 12, 10, 15, 11, 14]
    print_anf(L_a, 'ANF L_a')

    G_ag = comp2(G_g, inverse(L_a))
    print('Look up table of G_ag', G_ag, '\n')
    print_anf(G_ag, 'ANG G_ag')

    # The conjugate G_ag o S o G_ag^{-1} investigated in Appendix A
    S_conjugate = comp3(G_ag, SB0, inverse(G_ag))
    print('Look up table of S_conjugate', S_conjugate, '\n')

    # DDT of S_conjugate: the 0xd -> 0xd transition with probability 1 appears.
    for x in ddt(S_conjugate):
        print(x)

    # Test function verifying with some "assert" that:
    # 0xd --> 0xd holds with proba 1 for S_conjugate
    # 0xdddd --> holds with proba 1 for M_conjugate
    differential_study(G_ag, [0xd, 0xdddd])

    ####################################
    # A.3.4 Commutative Interpretation #
    ####################################
    diff = 0xd
    diff = bin(diff)[2:].zfill(4)[::-1]  # reversed b : b[0] = LSB

    n = 4
    v = ['x%d' % d for d in range(n)] + ['k%d' % d for d in range(n)]
    poly_ring = BooleanPolynomialRing(n * 2, v)
    poly_ring.inject_variables(verbose=False)

    anf_G_Tk_Gi = anf_conjugate_ark(G_ag)
    dico = dict(zip(v[:4], [poly_ring(x) + poly_ring(y) for (x, y) in zip(v[:4], diff)]))
    # dico = {x_i : x_i + c_i} where c_i is the ith bit of 0xd
    print('\nDerivative of G_Tk_Gi toward 0xd')
    for x in anf_G_Tk_Gi:  # G_Tk_Gi(x+0xd) + G_Tk_Gi(x)
        print(x.subs(dico) + x)
    print()

    A_1 = [15, 11, 13, 9, 14, 10, 12, 8, 7, 3, 5, 1, 6, 2, 4, 0]
    print_anf(A_1, 'ANF A_1 and Gi o T_0xd o G')
    anf_affine_a = algebraic_normal_form(A_1)

    anf_Gi_Tk_G = anf_conjugate_ark(inverse(G_ag))
    dico = dict(zip([poly_ring(x) for x in v[4:]], [int(x) for x in diff]))  # dico = {k_i: c_i}
    anf_Gi_add_0xd_G = [t.subs(dico) for t in anf_Gi_Tk_G]

    assert anf_Gi_add_0xd_G == anf_affine_a  # we get G_i o T_0xd o G == A_1
