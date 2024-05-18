//
// Created by Jules Baudrin on 02/01/2023.
// Cleaned up on 18/05/2024.
//
// This file contains some classes and enums useful for launching the experiments.
// The function step_by_step_observation declared at the last line is the most
// important one and is described in .cpp.
//

#ifndef COMMUTATIVE_PROPERTY_HPP
#define COMMUTATIVE_PROPERTY_HPP

#include "utils.hpp"
#include "midori.hpp"


#include <vector>
#include <omp.h>
#include <bit>
#include <set>
#include <map>
#include <fstream>
#include <ostream>
#include <filesystem>
#include <string>
#include <math.h>
#include <algorithm>

#define LOG2(X) (X?((unsigned) (8*sizeof (unsigned long long) - __builtin_clzll((X)) - 1)):0)

// A class to describe an activity pattern.
// nibbles is the list of indices of active nibbles
// activities is the list of sboxes to apply to each active nibble
// weak_keys is the list of weak keys for each active nibble. It is computed when initialized.
class Activity_pattern {
public:
	std::string label;
	std::vector<uint> nibbles;
	std::vector<std::vector<uint64_t>> activities;
	std::vector<std::vector<uint64_t>> weak_keys;

	Activity_pattern() {}

	Activity_pattern(std::vector<uint> n, std::vector<std::vector<uint64_t>> a, std::string s) : label(s), nibbles(n), activities(a) {
		for(uint i = 0; i < nibbles.size(); i++) {
			std::vector<uint64_t> wk;
			for(uint j = 0; j < activities[i].size(); j++) {
				if((activities[i][j] ^ activities[i][0]) == j)
					wk.insert(wk.end(), j);
			}
			weak_keys.insert(weak_keys.end(), wk);
		}
	}


	state apply(const state &s) const {
		state new_s = 0;
		for(int i = 0; i < 16; i++) {
			auto pt = std::find(nibbles.begin(), nibbles.end(), i);
			if(pt != nibbles.end()) {
				uint index = pt - nibbles.begin();
				new_s ^= SHIFT_TO_ITH_NIBBLE(activities[index][GET_ITH_NIBBLE(s, i)], i);
			}
			else
				new_s ^= SHIFT_TO_ITH_NIBBLE(GET_ITH_NIBBLE(s, i), i);
		}
		return new_s;
	}

	void print(std::ostream &stream_o) const {
		bool all_eq = true;
		for (const auto &item : activities) {
			if (item != activities[0]) {
				all_eq = false;
				break;
			}
		}
		if(all_eq) {
			stream_o << "pattern : " << label << std::hex;
			stream_o << "\tnibble ";
			for(uint i = 0; i < nibbles.size(); i++) {
				stream_o << nibbles[i] << " ";
			}
			stream_o << "| activity {";
			for (const auto &item : activities[0])
			stream_o << item << " ";
			stream_o << "} | wk {";
			for (const auto &item : weak_keys[0])
			stream_o << item << " ";
			stream_o << "}" << std::endl;
		}
		else {
			stream_o << "pattern : " << label << std::endl << std::hex;
			for(uint i = 0; i < nibbles.size(); i++) {
				stream_o << "\tnibble " << nibbles[i] << " | activity {";
				for(const auto &item: activities[i])
					stream_o << item << " ";
				stream_o << "} | wk {";
				for(const auto &item: weak_keys[i])
					stream_o << item << " ";
				stream_o << "}" << std::endl;
			}
		}
		stream_o << std::dec;
	}
};


// affine function such that A o SB0 = SB0 o A
const std::vector <uint64_t> affine_a = {15, 11, 13, 9, 14, 10, 12, 8, 7, 3, 5, 1, 6, 2, 4, 0};
// affine function such that B o SB0(x) = SB0 o B(x) with proba 10/16
const std::vector<uint64_t> affine_b = {4, 5, 6, 7, 0, 1, 2, 3, 10, 11, 8, 9, 14, 15, 12, 13};
// affine function x -> x XOR 15
const std::vector<uint64_t> diff_0xf {15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 0};

const std::vector<uint64_t> tic_proba_1 = {10, 6, 8, 4, 3, 15, 1, 13, 2, 14, 0, 12, 11, 7, 9, 5};
const std::vector<uint64_t> tac_proba_1 = {5, 12, 7, 14, 9, 0, 11, 2, 13, 4, 15, 6, 1, 8, 3, 10};

const std::vector<uint64_t> tic_proba_075 = {6, 15, 4, 13, 2, 11, 0, 9, 14, 7, 12, 5, 10, 3, 8, 1};
const std::vector<uint64_t> tac_proba_075 = {1, 0, 3, 2, 8, 9, 10, 11, 6, 7, 4, 5, 15, 14, 13, 12};

// Some useful activity patterns
const std::map<std::string, Activity_pattern> PATTERNS = {
		/* (A, id, A, id) o M(x) = M o (A, id, A, id)(x) with proba 2^{-4}  */
		{"square", Activity_pattern({0, 2, 8, 10}, {affine_a, affine_a, affine_a, affine_a}, "square")},
		/* Same as square, but with a shifted activity pattern  */
		{"square2", Activity_pattern({4, 6, 12, 14}, {affine_a, affine_a, affine_a, affine_a}, "square2")},
		/* Same as square2, but uses affine_b instead of affine_a */
		{"square_b", Activity_pattern({4, 6, 12, 14}, {affine_b, affine_b, affine_b, affine_b}, "square_b")},
		/* full_a */
		{"full_a", Activity_pattern({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}, std::vector<std::vector<uint64_t>>(16, affine_a), "full_a")},
		/* (B, B, B, B) o M(x) = M o (B, B, B, B)(x) with proba 1 */
		{"full_b", Activity_pattern({0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15}, std::vector<std::vector<uint64_t>>(16, affine_b), "full_b")},
		/* mixed ? ? */
		{"mixed", Activity_pattern({0, 2, 8, 10}, {affine_a, diff_0xf, affine_a, diff_0xf}, "mixed")},
		//
		{"tic_proba_1",  Activity_pattern({0, 2, 8, 10}, {tic_proba_1, tic_proba_1, tic_proba_1, tic_proba_1}, "tic_proba_1")},
		{"tac_proba_1",  Activity_pattern({0, 2, 8, 10}, {tac_proba_1, tac_proba_1, tac_proba_1, tac_proba_1}, "tac_proba_1")},
		//
		{"tic_proba_075",  Activity_pattern({0, 2, 8, 10}, {tic_proba_075, tic_proba_075, tic_proba_075, tic_proba_075}, "tic_proba_075")},
		{"tac_proba_075",  Activity_pattern({0, 2, 8, 10}, {tac_proba_075, tac_proba_075, tac_proba_075, tac_proba_075}, "tac_proba_075")},
};

// Different parallelization mode depending on which loop we want to parallelize
// (See .cpp)
enum ParallelMode {no_parallel, parallel_keys, parallel_plaintexts};
const std::map<ParallelMode, std::string> parallel_mode_names = {
		{no_parallel, "no_parallel"},
		{parallel_keys, "parallel_keys"},
		{parallel_plaintexts, "parallel_plaintexts"}
};

// Different round constant options.
enum RoundConstants {null, weak, standard};
const std::map<RoundConstants, std::string> round_constants_names = {
		{null, "null"},
		{weak, "weak"},
		{standard, "standard"}
};

// Different option regarding the results that are stored in result file.
enum OutputResults {out_no_result, out_fixed_key_results, out_overall_results};
const std::map<OutputResults, std::string> output_results_names = {
		{out_no_result, "out_no_result"},
		{out_fixed_key_results, "out_fixed_key_results"},
		{out_overall_results, "out_overall_results"},
};

// Different option regarding the results that are printed in terminal.
enum PrintResults {print_no_result, print_fixed_key_results, print_overall_results, print_plaintext_results};
const std::map<PrintResults, std::string> print_results_names = {
		{print_no_result, "print_no_result"},
		{print_fixed_key_results, "print_fixed_key_results"},
		{print_overall_results, "print_overall_results"},
		{print_plaintext_results, "print_plaintext_results"}
};

// The parameter class for launching an experiment.
class Parameters {
public:
	uint64_t whitening_key = ((uint64_t) 0); // Default : no whitening
	RoundConstants round_constants = null; // Default : no round constant
	std::vector<uint64_t> sbox = SB0; // Default : Midori Sbox (see midori.hpp)
	std::vector<uint64_t> shuffle_cells = SHIFT_ROWS; // Default : AES ShiftRows
	//Activity_pattern pattern = PATTERNS.at("square");
	std::vector<const Activity_pattern*> patterns;

	uint min_round_index = 0;
	uint max_round_index = 0;
	uint64_t nb_keys = 10;
	std::vector<uint64_t> nb_plaintexts_per_round;

	uint64_t master_seed = 0;
	std::string filename = "";
	ParallelMode parallel_mode = no_parallel;
	uint nb_threads = 1;

	OutputResults output_results = out_no_result;
	PrintResults print_res = print_fixed_key_results;
	bool print_diff = false;

	// WARNING : autofill is done only with respect to THE FIRST PATTERN
	void auto_fill_plaintexts_expected_success(uint log2_expected_success) {
		// Auto-fill of the nb of trials
		for(uint r = min_round_index; r <= max_round_index; r++) {
			uint log2_nb_plaintexts;
			if(patterns[0]->label == "square" || patterns[0]->label == "square2" || patterns[0]->label == "single_nibble" || patterns[0]->label == "tic_proba_1" || patterns[0]->label == "tac_proba_1")
				log2_nb_plaintexts =  (4 * (r - 1)) + log2_expected_success;
			else if(patterns[0]->label == "mixed")
				log2_nb_plaintexts =  (8 * (r - 1)) + 4 + log2_expected_success;
			else if(patterns[0]->label == "square_b")
				log2_nb_plaintexts = (7 * (r - 1)) + 3 + log2_expected_success;
			else if(patterns[0]->label == "tic_proba_075" || patterns[0]->label == "tac_proba_075")
				log2_nb_plaintexts = (6 * (r - 1)) + 2 + log2_expected_success;
			else
				log2_nb_plaintexts =  (11 * r) + log2_expected_success; //full ?
			uint64_t nb_plaintexts = ((uint64_t) 1) << log2_nb_plaintexts;
			nb_plaintexts_per_round.insert(nb_plaintexts_per_round.end(), nb_plaintexts);
		}
	}

	void random_new_seed(){
		// Randomize output files name
		std::random_device rd_seed;
		std::mt19937_64 rng(rd_seed());
		uint64_t master_seed = rng();
		std::string filename = "results/results_" + uint64_t_to_hex(master_seed) + "_v0.txt";
		while(std::filesystem::exists(filename)) {
			master_seed = rng();
			filename = "results/results_" + uint64_t_to_hex(master_seed) + "_v0.txt";
		}
		this->master_seed = master_seed;
	}

	void create_new_file_with_header(){
		uint version = 0;
		std::string filename = "results/results_" + uint64_t_to_hex(master_seed);
		while(std::filesystem::exists(filename + "_v" + std::to_string(version) + ".txt"))
			version++;
		filename += "_v" + std::to_string(version) + ".txt";
		this->filename = filename;
		std::fstream file(filename, file.out | file.app);
		this->print(file);
		file.close();
	}

	void print(std::ostream &stream_o) const {
		stream_o << "filename : " << filename << std::endl;
		stream_o << "seed : " << uint64_t_to_hex(master_seed) <<  std::endl;
		stream_o << "sbox : ";
		for (const auto &item : sbox)
			stream_o << item << " ";
		stream_o << std::endl;
		stream_o << "shuffle_cells : ";
		for (const auto &item : shuffle_cells)
			stream_o << item << " ";
		stream_o << std::endl;
		for (const auto &p : patterns)
			p->print(stream_o);
		stream_o << "constants : " << round_constants_names.at(round_constants) << std::endl;
		stream_o << "whitening_key : " << uint64_t_to_hex(whitening_key) << std::endl;

		// print round indices
		stream_o << "min_round_index : " << min_round_index << std::endl;
		stream_o << "max_round_index : " << max_round_index << std::endl;
		stream_o << "msg_per_round : ";
		for(uint i = min_round_index; i <= max_round_index; i++)
			stream_o << LOG2(nb_plaintexts_per_round[i-min_round_index]) << " ";
		stream_o << std::endl;
		stream_o << "nb_keys : " << nb_keys << std::endl;

		stream_o << "parallel_mode : " << parallel_mode_names.at(parallel_mode) << std::endl;
		stream_o << "nb_threads : " << nb_threads << std::endl;
		stream_o << "output_results : " << output_results_names.at(output_results) << std::endl;
		stream_o << "print_res : " << print_results_names.at(print_res) << std::endl;
		stream_o << "print_diff : " << print_diff << std::endl;
	}
};

void step_by_step_observation(const Parameters &p);
#endif //COMMUTATIVE_PROPERTY_HPP
