# PQ-ABDSRS: reproduction code

Code and LaTeX source for **Post-Quantum Attribute-Based Verifiable Data Storage and Retrieval for Cloud Computing Environments**.

Every number in the manuscript that was not taken from a cited paper is computed by the code in this repository. Nothing is hard-coded into the tables by hand.

## What this repository is, and is not

**It is** a reproduction artifact for the analytic results: the parameter derivation (Section 9.1), the concrete-hardness estimates (Table 5), the complete serialized-size accounting (Tables 7 and 8), and the two figures.

**It is not** an implementation of PQ-ABDSRS. No key generation, encryption, signing or verification is implemented. The manuscript states this in Section 1.3 and reports no measured benchmarks, and this repository does not contradict that. If you came here expecting a working cryptosystem, there is not one yet, and building one is listed as future work.

## Quick start

```bash
git clone https://github.com/keshavsinha/pq-abdsrs.git
cd pq-abdsrs
pip install -r requirements.txt

make numbers    # regenerate every table and figure into out/
make test       # check the code agrees with the numbers printed in the paper
make paper      # rebuild the PDF from paper/template.tex
```

`make numbers` writes:

| File | Contents |
|---|---|
| `out/table5_hardness.csv` | Table 5, concrete hardness of the LWE and SIS instances |
| `out/table7_sizes.csv` | Table 7, complete serialized sizes at ip-1 to ip-4 |
| `out/table8_breakdown.csv` | Table 8, ciphertext component breakdown |
| `out/size-params.png` | Figure 2 |
| `out/size-ciphertext.png` | Figure 3 |
| `out/summary.txt` | Human-readable digest of all of the above |

## Layout

```
src/pqabdsrs/
    params.py      parameter set, constraints C1-C3, core-SVP hardness estimation
    sizes.py       byte-level size model for every serialized object
    figures.py     Figures 2 and 3
    __main__.py    CLI: regenerates everything
tests/
    test_paper_claims.py   one assertion per number printed in the manuscript
paper/
    template.tex   manuscript source (MDPI class)
    Definitions/   MDPI class files
    Figures/       architecture diagram plus the two generated figures
```

## How the parameter set is derived

Three constraints fix it, and `src/pqabdsrs/params.py` encodes all three:

- **C1** TrapGen width, `m >= (1 + delta) n log2 q` with `delta = 1`, so `m = 2 n ceil(log2 q)` (Alwen and Peikert).
- **C2** SamplePre Gaussian, `sigma >= ||T~|| * omega(sqrt(log 2m))`.
- **C3** Decryption correctness, `B_dec < q/4` where `B_dec` is derived in Theorem 1 of the manuscript.

The result is `n = 1280`, `q = 2^27`, `m = 69,120`, `sigma = 1024`, giving `2^151` classical and `2^137` quantum core-SVP, with a correctness margin of `2^4.8`.

`SUPERSEDED_DRAFT` in `params.py` is the parameter set used in the pre-revision draft (`n = 512`). It is kept so that the manuscript's statement about it can be checked rather than taken on trust: running the same estimator on it gives block size 140, that is `2^41` classical and `2^37` quantum, which is not a secure parameter set at any level.

## Known limitations

Please read these before citing any number from this repository.

1. **Core-SVP is a lower-bound methodology.** `lwe_block_size` implements the primal-uSVP 2016 estimate. It does not model dual attacks, hybrid attacks, or the BKZ simulation used by the current lattice estimator. Before a final parameter set is fixed, run the [lattice estimator](https://github.com/malb/lattice-estimator) and use its output instead. The manuscript says the same thing in the caption of Table 5.
2. **Some sizes are lower bounds, by construction.** The ABS public parameters are not counted, and the ABS signature is costed at the GPV size, which is smaller than any real ABS signature. Both are noted in the manuscript captions. The true sizes are larger than reported.
3. **The size model assumes a clause width.** `CLAUSE_WIDTH = 5` in `sizes.py` sets how many attributes a DNF clause is assumed to contain, which affects only the policy-description bytes, a term of a few hundred bytes against a multi-megabyte total.
4. **Sizes are decimal.** 1 MB is `10^6` bytes, matching the manuscript.

## Reproducing a figure or number you do not trust

Each table has a single function behind it. To check the ciphertext total at ip-2 by hand:

```python
from pqabdsrs import LEVEL1
from pqabdsrs.sizes import POINTS, SizeModel, human

model = SizeModel(LEVEL1)
for name, value in model.ciphertext_breakdown(POINTS[1]).items():
    print(f"{name:<12} {human(value)}")
print("total       ", human(model.ciphertext(POINTS[1])))
```

## Citation

See `CITATION.cff`. If you use the size model or the parameter derivation, please cite the paper rather than this repository alone.

## License

Code is released under the MIT License (`LICENSE`). The manuscript text and figures in `paper/` are not covered by it; rights there follow the journal's agreement.
