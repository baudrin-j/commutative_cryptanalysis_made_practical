CC = g++-mp-12
PRODUCTFLAGS = -c -std=c++20 -Wall -Wextra -Wpedantic -O3 -march=native -Xpreprocessor -fopenmp

.SUFFIXES: .cpp .o

.cpp.o:; $(CC) -o $@ $(PRODUCTFLAGS) $<

test: midori.o utils.o midori_test.o
	$(CC) -o test.out $^

commutative: commutative_property.o utils.o midori.o command_line_parser.o
	$(CC) -fopenmp -o commutative.out $^

# Clean deletes .o files, clean_everything cleans everything, obviously
clean:
	rm -f  *.o
clean_everything:
	rm -f *.o *.out
