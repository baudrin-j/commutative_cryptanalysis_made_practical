# pip install tabulate (prints data in a nice table)
from tabulate import tabulate
from tqdm import tqdm
import itertools
import time

from sage.all_cmdline import *

from sboxU import self_affine_equivalent_mappings, tobin, linear_function_lut_to_matrix

from ciphers.cipher import AESLikeCipher
from ciphers.aes import AES
from ciphers.ascon import Ascon
from ciphers.boomslang import Boomslang
from ciphers.craft import Craft
from ciphers.gift import Gift
from ciphers.iscream import iScream
from ciphers.kuznechik import Kuznechik
from ciphers.led import LED
from ciphers.mantis import Mantis
from ciphers.midori import Midori
from ciphers.pride import Pride
from ciphers.prince import Prince
from ciphers.present import Present
from ciphers.rectangle import Rectangle
from ciphers.scream import Scream
from ciphers.skinny import Skinny
from ciphers.streebog import Streebog

print("### Setting up ciphers (this could take some time, as we have to convert finite field multiplication into matrix multiplication) ###", flush=True)

CIPHER_LIST = [AES(), Ascon(), Boomslang(), Craft(), Gift(64), Gift(128),
               iScream(), Kuznechik(), LED(), Mantis(), Midori(),
               Pride(), Prince(), Present(), Rectangle(), Scream(), Skinny(64),
               Skinny(128), Streebog()]  # Some take quite a bit of time, e.g., AES(), iScream(), Kuznechik(), Pride(), Rectangle(), Skinny(128), Streebog()

print("### Cipher setup done ###", flush=True)

class Trail:
    """
    Class for representing commutative trails
    """
    def __init__(self, L_in, c_in, L_out, c_out):
        self.L_in = L_in  # Linear part of affine map applied to the input
        self.c_in = c_in  # Constant of affine map applied to the input
        self.L_out = L_out  # Linear part of affine map applied to the output
        self.c_out = c_out  # Constant of affine map applied to the output

    @staticmethod
    def over_sbox(S, validate_results=False):
        """
        Returns all affine self equivalences of SBox S. If validate_results is set to true,
        then it is also checked that the affine equivalence holds for all inputs.
        """
        m = S.input_size()
        affine_equivalences = []
        for lut_in, lut_out in self_affine_equivalent_mappings(list(S)):
            c_in = vector(GF(2), tobin(lut_in[0], m))
            c_out = vector(GF(2), tobin(lut_out[0], m))
            L_in = linear_function_lut_to_matrix([l ^^ lut_in[0] for l in lut_in])
            L_out = linear_function_lut_to_matrix([l ^^ lut_out[0] for l in lut_out])
            L_out = L_out.inverse()
            c_out = L_out * c_out
            affine_equivalences.append(Trail(L_in, c_in, L_out, c_out))
        if validate_results:
            for x in GF(2)**m:
                for ae in affine_equivalences:
                    # Make sure that bit order is correct
                    assert ae.L_out * S(x) + ae.c_out == S(ae.L_in * x + ae.c_in)
        return affine_equivalences
    
    def __repr__(self):
        return f"L_in={self.L_in}, c_in={self.c_in}, L_out={self.L_out}, c_out={self.c_out}"

def find_two_round_trails(cipher):
    """
    Returns all two-round commutative trails for cipher, as well as the time required to do so
    """
    time_start = time.time()
    sbox_affine_equivalences = Trail.over_sbox(cipher.S)
    time_affine_equivalence = time.time() - time_start
    # Make use of super-box structure (if present)
    if isinstance(cipher, AESLikeCipher):
        linear_layer = cipher.mc_binary_matrix
        nbr_sboxes = cipher.nbr_sboxes // cipher.nbr_superboxes
    else:
        linear_layer = cipher.L
        nbr_sboxes = cipher.nbr_sboxes
    # Try to connect trails over the s-box layers over the linear layer
    trails = connect_over_linear_layer(sbox_affine_equivalences, linear_layer, nbr_sboxes, cipher.S.input_size())

    return trails, {"total": time.time() - time_start, "affine_equivalence": time_affine_equivalence}

def connect_over_linear_layer(sbox_affine_equivalences, L, nbr_sboxes, m):
    """
    Starting with all possible A, B such that S A = B S, return those such that
    L Diag(B_1,...,B_{n/m}) = Diag(A'_1,...,A'_{n/m}) L. In other words, return the
    cores of all trails over SBox-, linear- and SBox-layer.
    """
    assert (nbr_sboxes & (nbr_sboxes-1) == 0) and nbr_sboxes != 0  # Check that nbr_sboxes is a power of two
    nbr_blocks = nbr_sboxes
    size_block = m
    # Start with filtering based on m x m blocks L_ii (i.e. L_ii B = A' L_ii for S A = B S and S A' = B' S)
    block_wise_trail_cores = []
    for i in range(nbr_blocks):
        L_ii = L[i*size_block:(i+1)*size_block, i*size_block:(i+1)*size_block]
        trails = []
        for e1 in sbox_affine_equivalences:
            left_side = L_ii * e1.L_out  # precalculate the left side, as it will stay the same
            for e2 in sbox_affine_equivalences:
                # Filter based on L_ii
                if left_side == e2.L_in * L_ii:
                    # Note: The trail core uses the output map (of equivalence e1) as input and the input map (of equivalence e2) as output
                    trails.append(Trail(e1.L_out, e1.c_out, e2.L_in, e2.c_in))
        block_wise_trail_cores.append(trails)
        
    while True:
        # Combine blocks until only one is left
        nbr_blocks = nbr_blocks // 2
        size_block = size_block * 2
        # We are done if there is nothing left to combine
        if nbr_blocks == 0:
            break
        # Filter using bigger blocks
        tmp = block_wise_trail_cores
        block_wise_trail_cores = []
        for i in range(nbr_blocks):
            L_ii = L[i*size_block:(i+1)*size_block, i*size_block:(i+1)*size_block]
            trails = []
            for t1, t2 in itertools.product(tmp[2*i], tmp[2*i + 1]):
                L_in = block_diagonal_matrix(t1.L_in, t2.L_in)
                L_out = block_diagonal_matrix(t1.L_out, t2.L_out)
                if L_ii * L_in == L_out * L_ii:  # Check if for a given which B, A' (wrapped in a Trail object) the equation L_ii * B = A' * L_ii holds
                    trails.append(Trail(
                        L_in, vector(itertools.chain(t1.c_in, t2.c_in)),
                        L_out, vector(itertools.chain(t1.c_out, t2.c_out)),
                    ))
            block_wise_trail_cores.append(trails)
    # Filter constants
    trails = [t for t in block_wise_trail_cores[0] if L * t.c_in == t.c_out]
    return trails

if __name__ == "__main__":
    print("Checking for probability one trails over two rounds/superboxes")
    # Data for trails
    header = ["Cipher", "#Trail", "Input Maps", "Input Constants", "Output Maps", "Output Constants"]
    data = []
    # Data for elapsed time
    header_time = ["Cipher", "Finding Affine Self-Equivalences", "Total"]
    data_time = []

    try:
        progress = tqdm(CIPHER_LIST, bar_format='Progress: {bar:20}| ({n_fmt}/{total_fmt}) {postfix}')
        for cipher in progress:
            progress.set_postfix_str(f"currently checking {cipher.name}")
            two_round_trails, elapsed_time = find_two_round_trails(cipher)
            data_time.append([cipher.name, elapsed_time["affine_equivalence"], elapsed_time["total"]])
            for i, trail in enumerate(two_round_trails):
                data.append([cipher.name, i, trail.L_in, trail.c_in, trail.L_out, trail.c_out])
                # Save the results we got so far
                with open("res.txt", "w") as f:
                    f.write(tabulate(data, headers=header, tablefmt="grid"))
    except KeyboardInterrupt:
        pass

    # Print trail details
    print(tabulate(data, headers=header, tablefmt="grid"))
    # Print elapsed times
    print(tabulate(data_time, headers=header_time, tablefmt="grid"))
