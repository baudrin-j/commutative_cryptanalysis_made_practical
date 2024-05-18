//
// Created by Jules Baudrin on 12/11/2022.
// Cleaned up on 18/05/2024.
//

#include "utils.hpp"

using namespace std;

// Pretty print of a 64-bit state
void print_state(const state &s) {
	cout << std::hex;
	for(int i = 0; i < 4; i++) {
		for(int j = 0; j < 4; j++) {
			cout << GET_ITH_NIBBLE(s, j*4 + i);
		}
		cout << endl;
	}
	cout << std::dec;
}

// Return the hexadecimal representation (as a string) of a state of 64 bits.
string uint64_t_to_hex(const uint64_t &i)
{
	std::stringstream stream;
	stream << "0x" << std::setfill ('0') << std::setw(sizeof(uint64_t)*2) << std::hex << i;
	return stream.str();
}

// Given the LUT of a bijection, return the LUT of its inverse.
vector<uint64_t> inverse(const vector<uint64_t> &f) {
	vector<uint64_t> fi(f.size(), 0);

	for(uint i = 0; i < f.size(); i++)
		fi[f[i]] = i;
	return fi;
}

// Return the LUT of the composition f o g of two functions f, g given as LUT
vector<uint64_t> comp(const vector<uint64_t> &f, const vector<uint64_t> &g) {
	vector<uint64_t> res;
	for(uint i = 0; i < g.size(); ++i)
		res.insert(res.end(), f[g[i]]);
	return res;
}

// Let V = Span(2, 5, 8). Return a random state in V x ... x V (16 times)
state random_state_in_cartesian_v(mt19937_64 &rng) {
	return random_state_in_cartesian_product(rng, {2, 5, 8});
}

// Return a random state in V x ... x V (16 times) where V is a subspace of {0,1}^4.
// basis is a basis of V (represented on 4 bits)
state random_state_in_cartesian_product(mt19937_64 &rng, const vector<state> &basis) {
	state s = 0;
	for(int i = 0; i < 16; i++)
		s ^= SHIFT_TO_ITH_NIBBLE(random_state_in_subspace(rng, basis), i);
	return s;
}

// Return a random vector in a subspace from a basis of it
state random_state_in_subspace(mt19937_64 &rng, const vector<state> &basis) {
	state s = 0;
	for(const auto &x: basis) {
		if(rng() % 2)
			s ^= x;
	}
	return s;
}