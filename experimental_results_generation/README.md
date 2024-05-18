README.md
=========

This folder contains the code used to generate Figure 4 of our paper.
The experiments are coded in C++ using some features from **C++20** and **OpenMP**.

The experiments essentially keep track of 3 observations regarding "pattern differences" of the form A(x) + y. 

1. Are all the pattern differences 0 throughout the whole encryption ?
2. Are all the pattern differences 0 at the end of each round ? (possibly non-zero in the middle of some rounds) ?
3. Is the output pattern difference 0 ?

Cases 1) and 3) are depicted in Figure 4.



## Content of the folder
- `utils.cpp/hpp` : some utils functions
- `midori.cpp/hpp` : MIDORI implementation
- `commutative_property.cpp/hpp` : the core code of the experiments
- `command_liner_parser.cpp/hpp` : the handling of command line arguments
- `midori_test.cpp` : a basic test of the test vectors of the original MIDORI paper
- `Makefile : a basic makefile

## Advices
Make sure to:
- Install a compiler supporting C++20
- Install OpenMP library
- Modify the Makefile
- Create a subfolder named `results` which will contain the results files.

## Compiling and launching
After compiling with `make commutative` experiments can be launched for instance
using: `./commutative.out -plaintexts_2 18 -keys_2 13 -round 4 -pattern square -constants weak -print_res print_no_result -output out_fixed_key_results -parallel parallel_plaintexts -threads 8 -launch`. This command will recreate the experiment sumed up in the second sub-figure of Figure 4.

The arguments used here are described below. More can be found in `command_line_parser.cpp`

|  Arguments   |                                                           Explanation                                                            |
|--------------|----------------------------------------------------------------------------------------------------------------------------------|
| `plaintexts_2` | Log_2 of the number of plaintexts per key (here 2^18 plaintexts)                                                                 |
| `keys_2`       | Log_2 of the number of keys to try                                                                                               |
| `round`        | The index of the round to study                                                                                                               |
| `pattern`      | Activity pattern described in `commutative_property.hpp` (square corresponds to the pattern described in Sec 6.2.2 of our paper) |
| `print_res`    | What should be printed in terminal (see `commutative_property.hpp`)                                                                       |
| `output`       | What should be stored in the result file (see `commutative_property.hpp`)                                                                |
| `parallel`     | Parallel mode to use (see `commutative_property.hpp`)                                                                            |
| `threads`      | Number of threads                                                                                                                |
| `launch`       | If it is not added to the arguments, the experiment will not be launch and only the parameters will be printed.                     |
