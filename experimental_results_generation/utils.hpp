//
// Created by Jules Baudrin on 12/11/2022.
// Cleaned up on 18/05/2024.
//

#ifndef UTILS_HPP
#define UTILS_HPP

#include <random>
#include <iostream>
#include <iomanip>
#include <vector>

#ifndef TYPES
#define TYPES

#define GET_ITH_NIBBLE(s, i) ((s >> (4*(15-(i)))) & 0xf)
#define SHIFT_TO_ITH_NIBBLE(val, i) (((uint64_t) val) << (4*(15-(i))))

// The top-left-hand nibble is the most significant one.
// The bottom-right-hand nibble ist the least significant one.
using state = uint64_t;
using uint = unsigned int;
#endif //TYPES

void print_state(const state &s);
std::string uint64_t_to_hex(const uint64_t &i);

std::vector<uint64_t> inverse(const std::vector<uint64_t> &f);
std::vector<uint64_t> comp(const std::vector<uint64_t> &f, const std::vector<uint64_t> &g);

state random_state_in_cartesian_v(std::mt19937_64 &rng);
state random_state_in_cartesian_product(std::mt19937_64 &rng, const std::vector<uint64_t> &basis);
state random_state_in_subspace(std::mt19937_64 &rng, const std::vector<state> &basis);

#endif //UTILS_HPP
