//
// Created by Jules Baudrin on 11/11/2022.
// Cleaned up on 18/05/2024.
//
// It contains everything regarding MIDORI.
//
// Despite the name midori_round_function and midori_encryption are actually
// parameterizable with different sbox and cell permutation than the original ones.
//
// The function midori_test_suite verifies the test vectors from the original paper.
// It also serves as basic example.
//

#include "midori.hpp"

using namespace std;

// Apply to each nibble of the state s, the sbox given as LUT.
// Return the output state without modifying s.
state sbox_layer(const state &s, const vector<uint64_t> &sbox) {
	state new_s = 0;
	for(int i = 0; i < 16; i++) {
		new_s ^= SHIFT_TO_ITH_NIBBLE(sbox[GET_ITH_NIBBLE(s, i)], i);
	}
	return new_s;
}

// Return MC[s] where MC is the Midori MixColumns.
state mc(const state &s) {
	state new_s = 0;
	uint col, row;
	for(uint i = 0; i < 16; i++) { // index of the nibble
		col = i / 4;
		row = i % 4;
		for(uint j = 0; j < 4; j++) { // fill the ith nibble of new_s
			if(j != row)
				new_s ^= SHIFT_TO_ITH_NIBBLE(GET_ITH_NIBBLE(s, 4*col + j), i);
		}
	}
	return new_s;
}

// Shuffle the nibbles of the state s according to the permutation given as LUT.
// Return the output state without modifying s.
state shuffle_cells(const state &s, const vector<uint64_t> &perm) {
	state new_s = 0;
	for(int i = 0; i < 16; i++) {
		new_s ^= SHIFT_TO_ITH_NIBBLE(GET_ITH_NIBBLE(s, perm[i]), i);
	}
	return new_s;
}

// Generate the original Midori round-key sequence from the two halves k0||k1 of the master key.
// The original round constants are included to the round-key.
// They can be disabled with with_rd_csts=0.
const std::vector<uint64_t> midori_key_schedule(const state &k0, const state &k1, const bool &with_rd_csts) {
	std::vector<uint64_t> round_keys;
	for(int i = 0; i < 15; i++) {
		if(i % 2 == 0)
			round_keys.insert(round_keys.end(), k0);
		else
			round_keys.insert(round_keys.end(), k1);
		if(with_rd_csts)
			round_keys[i] ^= ROUND_CONSTANTS[i];
	}
	return round_keys;
}

// Apply AES-like round to the plaintext and return the output.
// output = ARK o MC o SC o SB (plaintext)
// The LUT of the sbox and the shuffle permutation are passed as parameters.
// So is the round-key sequence.
state midori_round_function(const state &plaintext,
                            const vector<uint64_t> &sbox,
                     const vector<uint64_t> &perm,
                     const state &round_key) {
	state s = sbox_layer(plaintext, sbox);
	s = shuffle_cells(s, perm);
	s = mc(s);
	s ^= round_key;
	return s;
}

// Apply a full AES-like encryption to the plaintext and return the output.
// The LUT of the sbox and the shuffle permutation are passed as parameters.
// So is the round-key sequence, the whitening key and the number of rounds.
// For the last round, on the Sbox layer is applied.
state midori_encryption(const state &plaintext,
						const uint &nb_rounds,
						const std::vector<uint64_t> &sbox,
						const vector<uint64_t> &perm,
						const vector<uint64_t> &round_keys,
						const state &whitening_key) {
	state s = plaintext ^ whitening_key;
	for(uint i = 0; i < nb_rounds - 1; i++)
		s = midori_round_function(s, sbox, perm, round_keys[i]);
	s = sbox_layer(s, sbox);
	s ^= whitening_key;
	return s;
}

// Test the midori test vector from the original paper
void midori_test_suite() {
	// From https://eprint.iacr.org/2015/1142.pdf Appendix A: Test Vectors (p.29)
	//
	// Test vector 0
	// Plaintext : 0000000000000000
	// Key : 00000000000000000000000000000000
	// Ciphertext : 3c9cceda2bbd449a
	//
	// Test vector 1
	// Plaintext : 42c20fd3b586879e
	// Key : 687ded3b3c85b3f35b1009863e2a8cbf
	// Ciphertext : 66bcdc6270d901cd
	state plaintext = 0;
	state k0 = 0;
	state k1 = 0;
	state output = midori_encryption(plaintext, 16, SB0, MIDORI_CELL_PERM, midori_key_schedule(k0, k1, true), k0 ^ k1);
	assert(((void)"Midori64 encryption test vector 0", output == 0x3c9cceda2bbd449a));

	plaintext = 0x42c20fd3b586879e;
	k0 = 0x687ded3b3c85b3f3;
	k1 = 0x5b1009863e2a8cbf;
	output = midori_encryption(plaintext, 16, SB0, MIDORI_CELL_PERM, midori_key_schedule(k0, k1, true), k0 ^ k1);
	assert(((void)"Midori64 encryption test vector 1", output == 0x66bcdc6270d901cd));
}
