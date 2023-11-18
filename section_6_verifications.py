# COMMUTATIVE CRYPTANALYSIS MADE PRACTICAL
# This file contains verifications for the content of Section 6: APPLICATIONS
# (Note that variables are indexed starting from 0 here, but starting from 1 in the paper)

from sboxU import *  # Available at https://github.com/lpp-crypto/sboxU

#region MIDORI CONSTANTS
# Midori Sbox
SB0 = [0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6]
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


def comp2(lut1, lut2):
    """ Return the LUT of the composition of 2 functions given as LUT."""
    return [lut1[lut2[x]] for x in range(len(lut2))]
#endregion


if __name__ == '__main__':
    ################################################
    # MAPPINGS A_1 A_2 A_3 AS DEFINED IN SECTION 5 #
    ################################################
    A1 = [15, 11, 13, 9, 14, 10, 12, 8, 7, 3, 5, 1, 6, 2, 4, 0]
    A2 = [5, 12, 7, 14, 9, 0, 11, 2, 13, 4, 15, 6, 1, 8, 3, 10]
    A3 = [10, 6, 8, 4, 3, 15, 1, 13, 2, 14, 0, 12, 11, 7, 9, 5]
    print_anf(A1, 'ANF A1')
    print_anf(A2, 'ANF A2')
    print_anf(A3, 'ANF A3')

    #################
    # SECTION 6.1.1 #
    #################
    assert comp2(A1, SB0) == comp2(SB0, A1)  # Line 513
    assert comp2(A2, SB0) == comp2(SB0, A3)  # Line 533
    assert comp2(A3, SB0) == comp2(SB0, A2)  # Line 533
    assert comp2(A2, A3) == A1  # Line 534
    assert comp2(A3, A2) == A1  # Line 534

    L_A1 = [A1[x] ^ A1[0] for x in range(16)]
    L_A2 = [A2[x] ^ A2[0] for x in range(16)]
    L_A3 = [A3[x] ^ A3[0] for x in range(16)]

    fix_L_A1 = [x for x in range(16) if x == L_A1[x]]
    fix_L_A2 = [x for x in range(16) if x == L_A2[x]]
    fix_L_A3 = [x for x in range(16) if x == L_A3[x]]
    assert fix_L_A1 == [0, 2, 5, 7, 8, 10, 13, 15]  # Line 518 V = <0x2, 0x5, 0x8>
    assert fix_L_A1 == fix_L_A2  # Line 534
    assert fix_L_A1 == fix_L_A3  # Line 534

    #################
    # SECTION 6.1.3 #
    #################
    U_internal_differences = [x ^ A1[x] for x in range(16)]
    assert all([x in [10, 15] for x in U_internal_differences])  # Line 564 + Line 577 0 \notin U
    assert U_internal_differences.count(10) == 8  # Line 565
    assert U_internal_differences.count(15) == 8  # Line 565

    #################
    # SECTION 6.3 #
    #################
    A6 = [0x6, 0xf, 0x4, 0xd, 0x2, 0xb, 0x0, 0x9, 0xe, 0x7, 0xc, 0x5, 0xa, 0x3, 0x8, 0x1]
    A7 = [0x1, 0x0, 0x3, 0x2, 0x8, 0x9, 0xa, 0xb, 0x6, 0x7, 0x4, 0x5, 0xf, 0xe, 0xd, 0xc]

    A6_S_xor_S_A7 = xor_lut(comp2(A6, SB0), comp2(SB0, A7))
    A7_S_xor_S_A6 = xor_lut(comp2(A7, SB0), comp2(SB0, A6))
    assert A6_S_xor_S_A7.count(0) == 12  # Line 669
    assert A7_S_xor_S_A6.count(0) == 12  # Line 669

    L_A6 = [A6[x] ^ A6[0] for x in range(16)]
    L_A7 = [A7[x] ^ A7[0] for x in range(16)]

    fix_L_A6 = [x for x in range(16) if x == L_A6[x]]
    fix_L_A7 = [x for x in range(16) if x == L_A7[x]]
    assert len(fix_L_A6) == 8  # Line 670
    assert len(fix_L_A7) == 4  # Line 670

    A8 = [0x4, 0x5, 0x6, 0x7, 0x0, 0x1, 0x2, 0x3, 0xa, 0xb, 0x8, 0x9, 0xe, 0xf, 0xc, 0xd]
    A8_S_xor_S_A8 = xor_lut(comp2(A8, SB0), comp2(SB0, A8))
    assert A8_S_xor_S_A8.count(0) == 10  # Line 686

    L_A8 = [A8[x] ^ A8[0] for x in range(16)]
    fix_L_A8 = [x for x in range(16) if x == L_A8[x]]
    assert len(fix_L_A8) == 8  # Line 686
    assert 1 in fix_L_A8  # Line 686
