//
// Created by Jules Baudrin on 14/04/2023.
// Cleaned up on 18/05/2024.
//

#include "command_line_parser.hpp"

using namespace std;

char* get_command_option(char ** begin, char ** end, const string & option) {
	char ** itr = std::find(begin, end, option); // check if option is present in the list
	if (itr != end && ++itr != end)
	{
		return *itr; // returns the next argument if it exists
	}
	return 0;
}


char* parse_bool(int argc, char* argv[], const string &option, bool* attribute) {
	char * cur_option = get_command_option(argv, argv + argc, option);
	if(cur_option)
		*attribute = strtoul(cur_option, NULL, 10) & 1;
	return cur_option;
}

char* parse_ul(int argc, char* argv[], const string &option, uint* attribute) {
	char * cur_option = get_command_option(argv, argv + argc, option);
	if(cur_option)
		*attribute = strtoul(cur_option, NULL, 10);
	return cur_option;
}

char* parse_ull(int argc, char* argv[], const string &option, uint64_t * attribute, const uint &base) {
	char * cur_option = get_command_option(argv, argv + argc, option);
	if(cur_option)
		*attribute = strtoull(cur_option, NULL, base);
	return cur_option;
}

template<typename Key>
void parse_enum(int argc, char* argv[], const string &option, const map<Key, string> &map_values_names, Key* attribute) {
	char *cur_option = get_command_option(argv, argv + argc, option);
	if(cur_option) {
		string str_cur_option(cur_option);
		for (const auto& [key, name]: map_values_names) {
			if(str_cur_option == name) {
				*attribute = key;
				break;
			}
		}
	}
}

Parameters parse_command_line(int argc, char* argv[], bool* launch) {
	Parameters params;

	char* round = parse_ul(argc, argv, "-round", &(params.min_round_index));
	params.max_round_index = params.min_round_index;
	if(!round) {
		parse_ul(argc, argv, "-min", &(params.min_round_index));
		parse_ul(argc, argv, "-min", &(params.max_round_index));

		parse_ul(argc, argv, "-max", &(params.max_round_index));
	}

	parse_ul(argc, argv, "-threads", &(params.nb_threads));

	parse_bool(argc, argv, "-print_diff", &(params.print_diff));

	parse_ull(argc, argv, "-keys", &(params.nb_keys), 10);
	parse_ull(argc, argv, "-whitening", &(params.whitening_key), 16);
	parse_ull(argc, argv, "-seed", &(params.master_seed), 16);
	if(!params.master_seed)
		params.random_new_seed();

	parse_enum(argc, argv, "-constants", round_constants_names, &(params.round_constants));
	parse_enum(argc, argv, "-output", output_results_names, &(params.output_results));
	parse_enum(argc, argv, "-print_res", print_results_names, &(params.print_res));
	parse_enum(argc, argv, "-parallel", parallel_mode_names, &(params.parallel_mode));

	// pattern
	char* cur_option = get_command_option(argv, argv + argc, "-pattern");
	if(cur_option) {
		string str_cur_option(cur_option);
		for(uint i = 0; i <= params.max_round_index; i++) {
			params.patterns.insert(params.patterns.end(), &(PATTERNS.at(str_cur_option)));
		}
	}

	cur_option = get_command_option(argv, argv + argc, "-pattern_a_b");

	if(cur_option) {
		string str_cur_option(cur_option);
		uint delimiter_pos = str_cur_option.find("+");
		string pattern_a = str_cur_option.substr(0, delimiter_pos);
		string pattern_b = str_cur_option.substr(delimiter_pos + 1, str_cur_option.size());
		cout << pattern_a << pattern_b << endl;
		for(uint i = 0; i <= params.max_round_index; i++) {
			if(i % 2 == 0)
				params.patterns.insert(params.patterns.end(), &(PATTERNS.at(pattern_a)));
			else
				params.patterns.insert(params.patterns.end(), &(PATTERNS.at(pattern_b)));
		}
	}

	cur_option = get_command_option(argv, argv + argc, "-expected_success");
	if(cur_option)
		params.auto_fill_plaintexts_expected_success(strtoul(cur_option, NULL, 10));
	else {
		uint nb_rounds = params.max_round_index - params.min_round_index + 1;
		params.nb_plaintexts_per_round.resize(nb_rounds);

		cur_option = get_command_option(argv, argv + argc, "-plaintexts_2");
		if(cur_option) {
			for(uint i = 0; i < nb_rounds; i++) {
				params.nb_plaintexts_per_round[i] = ((uint64_t) 1) << strtoul(cur_option, NULL, 10);
				cur_option++;
			}
		}
		else {
			cur_option = get_command_option(argv, argv + argc, "-plaintexts_10");
			if(cur_option) {
				for(uint i = 0; i < nb_rounds; i++) {
					params.nb_plaintexts_per_round[i] = strtoull(cur_option, NULL, 10);
					cur_option++;
				}
			}
			else {
				fill(params.nb_plaintexts_per_round.begin(), params.nb_plaintexts_per_round.end(), ((uint64_t) 0));
			}
		}
	}

	cur_option = get_command_option(argv, argv + argc, "-keys_2");
	if(cur_option) {
		params.nb_keys = ((uint64_t) 1) << strtoul(cur_option, NULL, 10);
	}

	//sbox TODO
	//shuffle_cells TODO
	string launch_str("-launch");
	if(find(argv, argv + argc, launch_str) != argv + argc)
		*launch = true;
	return params;
}


int main(int argc, char * argv[]) {
	midori_test_suite();

	bool launch = false;
	Parameters params = parse_command_line(argc, argv, &launch);
	params.print(cout);

	// Launch experiment
	if(launch) {
		if(params.output_results != out_no_result)
			params.create_new_file_with_header();
		step_by_step_observation(params);
	}
}
