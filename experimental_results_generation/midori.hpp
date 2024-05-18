//
// Created by Jules Baudrin on 11/11/2022.
// Cleaned up on 18/05/2024.
//

#ifndef MIDORI_HPP
#define MIDORI_HPP

#include <assert.h>
#include <stdint.h>
#include <iostream>
#include <iomanip>
#include <vector>

#ifndef TYPES
#define TYPES

#define GET_ITH_NIBBLE(s, i) ((s >> (4*(15-(i)))) & 0xf)
#define SHIFT_TO_ITH_NIBBLE(val, i) (uint64_t(val) << (4*(15-(i))))

// The top-left-hand nibble is the most significant one.
// The bottom-right-hand nibble ist the least significant one.
using state = uint64_t;
using uint = unsigned int;
#endif //TYPES

// Midori Sbox
const std::vector<uint64_t> SB0 = {0xc,0xa,0xd,0x3,0xe,0xb,0xf,0x7,0x8,0x9,0x1,0x5,0x0,0x2,0x4,0x6};
// Midori cell permutation
const std::vector<uint64_t> MIDORI_CELL_PERM = {0, 10, 5, 15, 14, 4, 11, 1, 9, 3, 12, 6, 7, 13, 2, 8};
// AES ShiftRows
const std::vector<uint64_t> SHIFT_ROWS = {0, 5, 10, 15, 4, 9, 14, 3, 8, 13, 2, 7, 12, 1, 6, 11};
// Midori original round constants
const std::vector<uint64_t> ROUND_CONSTANTS = {
		0x0001010110110011,
		0x0111100011000000,
		0x1010010000110101,
		0x0110001000010011,
		0x0001000001001111,
		0x1101000101110000,
		0x0000001001100110,
		0x0000101111001100,
		0x1001010010000001,
		0x0100000010111000,
		0x0111000110010111,
		0x0010001010001110,
		0x0101000100110000,
		0x1111100011001010,
		0x1101111110010000};

//region Midori modified constants used in our paper.
const std::vector<uint64_t> WEAK_ROUND_CONSTANTS = {
		0x0002020220220022,
		0x0222200022000000,
		0x2020020000220202,
		0x0220002000020022,
		0x0002000002002222,
		0x2202000202220000,
		0x0000002002200220,
		0x0000202222002200,
		0x2002020020000002,
		0x0200000020222000,
		0x0222000220020222,
		0x0020002020002220,
		0x0202000200220000,
		0x2222200022002020,
		0x2202222220020000};
//endregion

state mc(const state &s);
state shuffle_cells(const state &s, const std::vector<uint64_t> &perm);
state sbox_layer(const state &s, const std::vector<uint64_t> &sbox);
const std::vector<uint64_t> midori_key_schedule(const state &k0,
												const state &k1,
												const bool &with_rd_csts);
state midori_round_function(const state &plaintext,
                            const std::vector<uint64_t> &sbox,
                            const std::vector<uint64_t> &perm,
                            const state &round_key);
state midori_encryption(const state &plaintext,
                        const uint &nb_rounds,
                        const std::vector<uint64_t> &sbox,
                        const std::vector<uint64_t> &perm,
                        const std::vector<uint64_t> &round_keys,
                        const state &whitening_key);

void midori_test_suite();

#endif //MIDORI_HPP
