# Commutative Cryptanalysis Made Practical - Supplementary Material

This repository contains supplementary material provided with [our paper]([xxx](https://tosc.iacr.org/)) published in
Volume 2023, Issue 4 of [*IACR Transactions on Symmetric Cryptology*](https://tosc.iacr.org/).

## Dependencies
 The publicly-available [SboxU library](https://github.com/lpp-crypto/sboxU) is used in some of the files.
 It contains various useful routines for analyzing S-boxes and Boolean functions,
 such as the ```self_affine_equivalent_mappings``` which was added during this project.
 
 Both ```section_6_verifications.py``` and ```appendix_verifications.py``` were developed with [Python] 3.10(https://www.python.org/) and [SageMath](https://www.sagemath.org/index.html) 9.7.

 ## Content
 - ```section_6_verifications.py``` enables to assess some easily-computer-verified statements made in Section 6.
 - ```appendix_verifications.py``` does the same for Appendix A.

## Authors
- Jules Baudrin
- Patrick Felke
- Gregor Leander
- Patrick Neumann
- Léo Perrin
- Lukas Stennes
