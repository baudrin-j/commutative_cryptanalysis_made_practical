//
// Created by Jules Baudrin on 02/01/2023.
// Cleaned up on 18/05/2024.
//
// Contains everything regarding the experiments.
// Lines 1 -> 165 contain auxiliary functions and are not so interesting.
//
//

#include "commutative_property.hpp"


#pragma omp declare reduction(coor_wise_add : std::vector<uint64_t> : \
                              std::transform(omp_out.begin(), omp_out.end(), omp_in.begin(), omp_out.begin(), std::plus<uint64_t>())) \
                    initializer(omp_priv = decltype(omp_orig)(omp_orig.size()))


using namespace std;

//region Print functions
string str_nibble(const uint &n, const bool &dot_0_option){
	if(n || !dot_0_option) {
		stringstream sstream;
		sstream << hex << n;
		return sstream.str();
	}
	else
		return ".";
}

void print_state_activity_pattern_inline(const state &s, const Activity_pattern *pattern, const bool &dot_0_option) {
	cout << std::hex;
	for(int i = 0; i < 16; i++) {
		auto pt = find(pattern->nibbles.begin(), pattern->nibbles.end(), i);
		if(pt != pattern->nibbles.end())
			cout << "\033[1;31m" << str_nibble(GET_ITH_NIBBLE(s, i), dot_0_option) << "\033[0m";
		else
				cout << str_nibble(GET_ITH_NIBBLE(s, i), dot_0_option);
	}
	cout << dec << " ";
}

/*
 * If print_diff_option == 1, prints the pair of state s0 and s1.
 * Otherwise, do nothing.
 */
void print_pair_of_states(const state &s0, const state &s1, const Activity_pattern *pattern, const bool &print_diff_option, const string &label){
	if(print_diff_option) {
		cout << "\t" << label << "\t";
		print_state_activity_pattern_inline(s0, pattern, false);
		cout << "\t";
		print_state_activity_pattern_inline(s1, pattern, false);
		cout << endl;
	}
}
//endregion

//region Functions used to save the overall results during step_by_step_observation when the keys are parallelized
void update_overall_results(const Parameters &p, vector<uint64_t> &final_0_diff_overall, vector<uint64_t> &all_0_diff_overall, vector<uint64_t> &all_end_round_0_diff_overall, \
const uint64_t &final_0_diff_per_key, const uint64_t &all_0_diff_per_key, const uint64_t &all_end_round_0_diff_per_key, const uint &r) {
	if(p.output_results == out_overall_results || p.print_res == print_overall_results) {
		// no need for critical thanks to reduction ?
		final_0_diff_overall[r] += final_0_diff_per_key;
		all_0_diff_overall[r] += all_0_diff_per_key;
		all_end_round_0_diff_overall[r] += all_end_round_0_diff_per_key;
	}
}


void save_overall_aux(const Parameters &p, const vector<uint64_t> &final_0_diff_overall, const vector<uint64_t> &all_0_diff_overall, const vector<uint64_t> &all_end_round_0_diff_overall, ostream &stream_o) {
	for(uint i = p.min_round_index; i <= p.max_round_index; i++) {
		stream_o << final_0_diff_overall[i] << " ";
		stream_o << all_0_diff_overall[i] << " ";
		stream_o << all_end_round_0_diff_overall[i] << " ";
		stream_o << "| ";
		stream_o << endl;
	}
}

void save_or_print_overall_results(const Parameters &p, const vector<uint64_t> &final_0_diff_overall, const vector<uint64_t> &all_0_diff_overall, const vector<uint64_t> &all_end_round_0_diff_overall) {
	if(p.output_results == out_overall_results) {
		fstream file(p.filename, file.out | file.app);
		save_overall_aux(p, final_0_diff_overall, all_0_diff_overall, all_end_round_0_diff_overall, file);
		file.close();
	}
	if(p.print_res == print_overall_results)
		save_overall_aux(p, final_0_diff_overall, all_0_diff_overall, all_end_round_0_diff_overall, cout);
}
//endregion

//region Functions used to save the fixed-key results
void update_fixed_key_results(const Parameters &p, string &str_fixed_key_results, const uint64_t &final_0_diff_per_key, \
const uint64_t &all_0_diff_per_key, const uint64_t &all_end_round_0_diff_per_key) {
	if(p.print_res == print_fixed_key_results || p.output_results == out_fixed_key_results) {
		str_fixed_key_results += to_string(final_0_diff_per_key) + " " + \
                        to_string(all_0_diff_per_key) + " " + \
                        to_string(all_end_round_0_diff_per_key) + " | ";
	}

	if(p.print_res == print_fixed_key_results) {
#pragma omp critical
		{
			cout << str_fixed_key_results << endl;
		}
	}
}

void save_fixed_key_results(const Parameters &p, const string &str_fixed_key_results) {
	if(p.output_results == out_fixed_key_results) {
#pragma omp critical
		{
			fstream file(p.filename, file.out | file.app);
			file << str_fixed_key_results << endl;
			file.close();
		}
	}
}
//endregion

//region Midori key schedule with possibly modified constants
const std::vector<uint64_t> midori_key_schedule_weak_round_csts(const state &k0, const state &k1, const RoundConstants &rd_csts) {
	std::vector<uint64_t> round_keys;
	for(int i = 0; i < 15; i++) {
		if(i % 2 == 0)
			round_keys.insert(round_keys.end(), k0);
		else
			round_keys.insert(round_keys.end(), k1);
		if(rd_csts == weak)
			round_keys[i] ^= WEAK_ROUND_CONSTANTS[i];
		else if(rd_csts == standard)
			round_keys[i] ^= ROUND_CONSTANTS[i];
	}
	return round_keys;
}
//endregion

// region Random weak-key generation
/**
 * Random weak key generating function.
 * @param rng A Mersenne Twister pseudo-random generator.
 * @param pattern The activity pattern from which weak key is derived.
 * @return A random weak key of 64 bits with respect to a given pattern.
 * Each nibble is taken randomly from the corresponding weak-key space.
 */
state random_weak_key(mt19937_64 &rng, const Activity_pattern &pattern) {
	state k = ((uint64_t)0);
	for(uint i = 0; i < 16; i++) {
		auto pt = find(pattern.nibbles.begin(), pattern.nibbles.end(), i);
		if(pt != pattern.nibbles.end()) {
			// if i is an active nibble, put a weak nibble
			uint index = pt - pattern.nibbles.begin();
			k = (k << 4) | pattern.weak_keys[index][rng() % pattern.weak_keys[index].size()];
		}
		else {
			// otherwise, put a random nibble
			k = (k << 4) | (rng() % 16);
		}
	}
	return k;
}
//endregion


//region CORE FUNCTIONS

/**
 * Computes the "pattern difference" of s0 and s1: A(s0) ^ s1 and returns it.
 * The pattern diff and usual diff s0^s1 are printed according to the value of
 * print_diff_option
 */
state diff(const state &s0, const state &s1, const Activity_pattern *pattern, const bool &print_diff_option, const string &label) {
	const state pattern_diff = pattern->apply(s0) ^ s1;

	if(print_diff_option) {
		const state diff = s0 ^ s1;
		cout << "\t" << label << "\t";
		if(pattern_diff) {
			print_state_activity_pattern_inline(pattern_diff, pattern, true);
		} else
			cout << "................";
		cout << "\t";
		if(diff) {
			print_state_activity_pattern_inline(diff, pattern, true);
		} else
			cout << "................";
		cout << endl;
	}
	return pattern_diff;
}

/**
* This function keep track of 3 observations regarding pattern differences of the form A(x) ^ y.
* 	1) all_0_diff is true iff the pattern differences are 0 throughout the whole encryption
* 	2) all_end_round_0_diff is true iff the pattern differences are 0 at the end of each round
* 	  (but it can be != 0 in the middle of the round)
* 	3) final_0_diff is true iff the output pattern difference is 0, regardless of the intermediate steps
 **/
void step_by_step_diff(const Parameters &p,
						const vector<state> &round_keys, const uint &nb_rounds, \
						const state &p0, const state &p1, state &c0, state &c1, bool &all_0_diff, \
						bool &final_0_diff, bool &all_end_round_0_diff, const bool &print_diff_option) {
	all_0_diff = true;
	all_end_round_0_diff = true;

	state s0 = p0 ^ p.whitening_key;
	state s1 = p1 ^ p.whitening_key;
	state d;

	print_pair_of_states(s0, s1, p.patterns[0], print_diff_option, "p0 & p1  ");
	all_0_diff &= (diff(s0, s1, p.patterns[0], print_diff_option, "input S " ) == 0);

	for(uint i = 1; i < nb_rounds; i++) {
		s0 = sbox_layer(s0, p.sbox);
		s1 = sbox_layer(s1, p.sbox);
		all_0_diff &= (diff(s0, s1, p.patterns[i], print_diff_option, "input SR") == 0);

		s0 = shuffle_cells(s0, p.shuffle_cells);
		s1 = shuffle_cells(s1, p.shuffle_cells);
		all_0_diff &= (diff(s0, s1, p.patterns[i], print_diff_option, "input MC") == 0);

		s0 = mc(s0);
		s1 = mc(s1);
		all_0_diff &= (diff(s0, s1, p.patterns[i], print_diff_option, "input AC") == 0);

		s0 ^= round_keys[i];
		s1 ^= round_keys[i];
		d = diff(s0, s1, p.patterns[i], print_diff_option, "input S ");
		all_0_diff &= (d == 0);
		all_end_round_0_diff &= (d == 0);
	}

	s0 = sbox_layer(s0, p.sbox);
	s1 = sbox_layer(s1, p.sbox);

	s0 ^= p.whitening_key;
	s1 ^= p.whitening_key;

	c0 = s0;
	c1 = s1;

	d = diff(s0, s1, p.patterns[nb_rounds], print_diff_option, "output S ");
	print_pair_of_states(s0, s1, p.patterns[nb_rounds], print_diff_option, "c0 & c1  ");
	final_0_diff = (d == 0);
	all_0_diff &= final_0_diff;
	all_end_round_0_diff &= final_0_diff;
}


// This function is rather hard to read but contains the logic to launch
// experiments according to the Parameters passed.
// Essentially, it tracks the three events described in step_by_step_diff (just above)
// for random keys and random plaintexts.
// It handles parallelization of the keys loop or the plaintexts loop depending
// on the needs.
void step_by_step_observation(const Parameters &p) {
	omp_set_num_threads(p.nb_threads);

	// Random machinery
	mt19937_64 master_rng(p.master_seed);
	// one random number generator per thread
	vector <mt19937_64> rng_threads;
	for(uint i = 0; i < p.nb_threads; i++)
		rng_threads.insert(rng_threads.end(), mt19937_64(master_rng()));

	// used only when output_results == overall_results
	uint size = 0;
	if(p.output_results == out_overall_results || p.print_res == print_overall_results)
		size = p.max_round_index + 1;
	vector<uint64_t> final_0_diff_overall(size, 0);
	vector<uint64_t> all_0_diff_overall(size, 0);
	vector<uint64_t> all_end_round_0_diff_overall(size, 0);

#pragma omp parallel for default(none) shared(std::cout, rng_threads, p)  reduction(coor_wise_add:final_0_diff_overall) reduction(coor_wise_add:all_0_diff_overall) reduction(coor_wise_add:all_end_round_0_diff_overall) if(p.parallel_mode == parallel_keys)
	for(uint64_t i_key = 0; i_key < p.nb_keys; i_key++) {
		uint keys_thread_index = 0;
		if(p.parallel_mode == parallel_keys)
			keys_thread_index = omp_get_thread_num();

		state k0 = random_weak_key(rng_threads[keys_thread_index], *(p.patterns[0])); // k0 is a weak key for first pattern
		state k1 = random_weak_key(rng_threads[keys_thread_index], *(p.patterns[1])); // k1 is a weak key for second pattern
		vector<uint64_t> round_keys = midori_key_schedule_weak_round_csts(k0, k1, p.round_constants);

		string fixed_key_results = uint64_t_to_hex(k0) + " " + uint64_t_to_hex(k1) + " | ";
		if(p.parallel_mode != parallel_keys &&  p.print_res == print_plaintext_results)
			cout << "---------------------------------" << endl;

		for(uint i_round = p.min_round_index; i_round <= p.max_round_index; i_round++) {
			uint64_t final_0_diff_per_key = 0;
			uint64_t all_0_diff_per_key = 0;
			uint64_t all_end_round_0_diff_per_key = 0;

#pragma omp parallel for default(none) shared(std::cout, rng_threads, round_keys, i_round, p, keys_thread_index) reduction(+:final_0_diff_per_key) reduction(+:all_0_diff_per_key) reduction(+:all_end_round_0_diff_per_key) if(p.parallel_mode == parallel_plaintexts)
			for(uint64_t i_plaintext = 0; i_plaintext < p.nb_plaintexts_per_round[i_round - p.min_round_index]; i_plaintext++) {
				uint plaintexts_thread_index = 0;
				if(p.parallel_mode == parallel_plaintexts)
					plaintexts_thread_index = omp_get_thread_num();
				if(p.parallel_mode == parallel_keys)
					plaintexts_thread_index = keys_thread_index;

				state p0, c0;
				state p1, c1;
				do {
					p0 = rng_threads[plaintexts_thread_index]();
					p1 = p.patterns[0]->apply(p0); // initial pattern is used
				} while(p0 == p1);

				bool all_0_diff = false;
				bool all_end_round_0_diff = false;
				bool final_0_diff = false;
				step_by_step_diff(p, round_keys, i_round, p0, p1, c0, c1, \
				all_0_diff, final_0_diff, all_end_round_0_diff, false);

				all_0_diff_per_key += all_0_diff;
				all_end_round_0_diff_per_key += all_end_round_0_diff;
				final_0_diff_per_key += final_0_diff;

				// if no_parallel and p.print_diff, go a second time through the round to print the differences
				if(p.parallel_mode == no_parallel && p.print_diff && final_0_diff && !all_0_diff) {
					cout << endl << endl << endl;
					step_by_step_diff(p, round_keys, i_round, p0, p1, c0, c1, \
				all_0_diff, final_0_diff, all_end_round_0_diff, true);
				}
				if(p.parallel_mode != parallel_keys && p.print_res == print_plaintext_results && all_0_diff) {
#pragma omp critical
					{
						cout << uint64_t_to_hex(p0) << endl;
					}
				}
			}
			update_fixed_key_results(p, fixed_key_results, final_0_diff_per_key, all_0_diff_per_key, all_end_round_0_diff_per_key);
			update_overall_results(p, final_0_diff_overall, all_0_diff_overall, all_end_round_0_diff_overall, final_0_diff_per_key, all_0_diff_per_key, all_end_round_0_diff_per_key, i_round);
		}
			save_fixed_key_results(p, fixed_key_results);
	}
	save_or_print_overall_results(p, final_0_diff_overall, all_0_diff_overall, all_end_round_0_diff_overall);
}
