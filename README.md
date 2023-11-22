# Commutative Cryptanalysis Made Practical - Supplementary Material

This repository contains supplementary material provided with [our paper]([xxx](https://tosc.iacr.org/)) published in
Volume 2023, Issue 4 of [*IACR Transactions on Symmetric Cryptology*](https://tosc.iacr.org/).

## Dependencies
 The publicly-available [SboxU library](https://github.com/lpp-crypto/sboxU) is used in some of the files.
 It contains various useful routines for analyzing S-boxes and Boolean functions,
 such as the ```self_affine_equivalent_mappings``` function which was added during this project.
 
 All scripts were developed with [Python] 3.10(https://www.python.org/) and [SageMath](https://www.sagemath.org/index.html) 9.7.
 ```algorithm_1.sage``` additionally requires the python packages ```tabulate``` and ```tqdm``` to be installed.

 ## Content
 - ```section_6_verifications.py``` enables to assess some easily-computer-verified statements made in Section 6.
 - ```appendix_verifications.py``` does the same for Appendix A.
 - ```algorithm_1.sage``` runs Algorithm 1 for the ciphers listed in Section 5. This script makes use of the cipher implementations from ```Beierle, C., Felke, P., Leander, G., Neumann, P., Stennes, L. (2023). On Perfect Linear Approximations and Differentials over Two-Round SPNs. In: Handschuh, H., Lysyanskaya, A. (eds) Advances in Cryptology – CRYPTO 2023. CRYPTO 2023. Lecture Notes in Computer Science, vol 14083. Springer, Cham.``` [https://doi.org/10.1007/978-3-031-38548-3_8](https://doi.org/10.1007/978-3-031-38548-3_8), which can be found at [https://doi.org/10.5281/zenodo.7934977](https://doi.org/10.5281/zenodo.7934977).

## Authors
- Jules Baudrin
- Patrick Felke
- Gregor Leander
- Patrick Neumann
- Léo Perrin
- Lukas Stennes
