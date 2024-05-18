//
// Created by Jules Baudrin on 14/04/2023.
// Cleaned up on 18/05/2024.
//

#ifndef COMMAND_LINE_PARSER_HPP
#define COMMAND_LINE_PARSER_HPP

#include "commutative_property.hpp"
#include <map>

char* get_command_option(char ** begin, char ** end, const std::string & option);
char* parse_bool(int argc, char* argv[], const std::string &option, bool* attribute);
char* parse_ul(int argc, char* argv[], const std::string &option, uint* attribute);
char* parse_ull(int argc, char* argv[], const std::string &option, uint64_t * attribute);
template<typename Key>
void parse_enum(int argc, char* argv[], const std::string &option, const std::map<Key, std::string> &map_values_names, Key* attribute);
Parameters parse_command_line(int argc, char* argv[], bool* launch);

#endif //COMMAND_LINE_PARSER_HPP
