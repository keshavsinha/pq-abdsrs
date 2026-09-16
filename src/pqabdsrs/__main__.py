"""
Regenerate every number and figure in the PQ-ABDSRS manuscript.

    python -m pqabdsrs --outdir out

Writes:
    out/table5_hardness.csv       Table 5, concrete hardness
    out/table7_sizes.csv          Table 7, complete serialized sizes
    out/table8_breakdown.csv      Table 8, ciphertext component breakdown
    out/size-params.png           Figure 2
    out/size-ciphertext.png       Figure 3
    out/summary.txt               human-readable digest of all of the above
"""

from __future__ import annotations

import argparse
import csv
import math
import os

from .figures import generate as generate_figures
from .params import LEVEL1, SUPERSEDED_DRAFT, core_svp_bits, hardness_table
from .sizes import (ABDSRS_CIPHERTEXT, ABDSRS_DECRYPTION_KEY,
                    ABDSRS_PUBLIC_PARAMS, SizeModel, human)


def write_csv(path, fieldnames, rows):
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({k: row.get(k) for k in fieldnames})


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--outdir", default="out")
    args = parser.parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    ps = LEVEL1
    model = SizeModel(ps)
    lines = []

    def say(text=""):
        print(text)
        lines.append(text)

    say("PQ-ABDSRS: regenerated parameters, hardness and sizes")
    say("=" * 66)
    say()
    say("Section 9.1  Parameter set")
    say("-" * 66)
    say(f"  n                      {ps.n}")
    say(f"  q                      2^{ps.log_q}")
    say(f"  m = 2 n ceil(log2 q)   {ps.m:,}")
    say(f"  2m                     {2 * ps.m:,}")
    say(f"  sigma                  {ps.sigma}")
    say(f"  error parameter s_e    {ps.s_e}  (std {ps.std_e:.3f})")
    say(f"  kappa                  {ps.kappa}")
    say(f"  ||T~||                 {ps.gs_norm:.1f}")
    say(f"  C2 satisfied           {ps.check_sigma()}")
    say(f"  B_dec (Eq. 2)          2^{math.log2(ps.noise_bound()):.1f}")
    say(f"  q/4                    2^{ps.log_q - 2}")
    say(f"  C3 margin              2^{ps.correctness_margin_bits():.1f}"
        f"   ({'OK' if ps.correctness_margin_bits() > 0 else 'FAILS'})")
    say()

    say("Table 5  Concrete hardness (primal-uSVP core-SVP)")
    say("-" * 66)
    rows = hardness_table(ps)
    for row in rows:
        beta = "---" if row["beta"] is None else f"2^{math.log2(row['beta']):.1f}"
        bs = str(row["block_size"]) if row["exact"] else ">1400"
        prefix = "" if row["exact"] else ">"
        say(f"  {row['instance']:<24} beta={beta:<8} b={bs:<6} "
            f"classical {prefix}2^{row['classical_bits']:.0f}  "
            f"quantum {prefix}2^{row['quantum_bits']:.0f}")
    write_csv(os.path.join(args.outdir, "table5_hardness.csv"),
              ["instance", "beta", "block_size", "dim",
               "classical_bits", "quantum_bits", "exact"], rows)
    say()

    say("Superseded draft parameter set, for comparison (Section 9.1)")
    say("-" * 66)
    old = SUPERSEDED_DRAFT
    b_old, _ = old.lwe_block_size()
    c_old, q_old = core_svp_bits(b_old)
    say(f"  n={old.n}, q=2^{old.log_q}: block size {b_old}, "
        f"classical 2^{c_old:.0f}, quantum 2^{q_old:.0f}")
    say(f"  the draft also stated m ~ 6,900, whereas 5 n log2 q = "
        f"{5 * old.n * old.log_q:,}")
    say()

    say("Table 7  Complete serialized sizes")
    say("-" * 66)
    table = model.table()
    for i, row in enumerate(table):
        say(f"  {row['label']}  |U|={row['universe']}  "
            f"ell_e={row['clauses']}  varsigma={row['keywords']}")
        say(f"     public params expanded   {human(row['public_params']):>12}"
            f"   ratio {row['public_params_ratio']:.2e}"
            f"   (ABDSRS {ABDSRS_PUBLIC_PARAMS:,} B)")
        say(f"     public params seeded     {human(row['public_params_seeded']):>12}")
        say(f"     decryption key           {human(row['decryption_key']):>12}"
            f"   ratio {row['decryption_key_ratio']:.0f}x"
            f"   (ABDSRS {ABDSRS_DECRYPTION_KEY[i]:,} B)")
        say(f"     ciphertext               {human(row['ciphertext']):>12}"
            f"   ratio {row['ciphertext_ratio']:.0f}x"
            f"   (ABDSRS {ABDSRS_CIPHERTEXT[i]:,} B)")
        say(f"     keyword trapdoor         {human(row['keyword_trapdoor']):>12}")
        say(f"     transformed ciphertext   {human(row['transformed_ciphertext']):>12}")
        say()
    write_csv(os.path.join(args.outdir, "table7_sizes.csv"),
              ["label", "universe", "clauses", "keywords", "public_params",
               "public_params_seeded", "public_params_ratio", "decryption_key",
               "decryption_key_ratio", "ciphertext", "ciphertext_ratio",
               "keyword_trapdoor", "transformed_ciphertext"], table)

    say("Table 8  Ciphertext component breakdown")
    say("-" * 66)
    header = f"  {'component':<28}" + "".join(f"{r['label']:>12}" for r in table)
    say(header)
    keys = [("CP-ABE clause ciphertexts", "cpabe"),
            ("keyword ciphertext", "keyword"),
            ("signature", "signature"),
            ("digests", "digests"),
            ("headers, AEAD, policies", "headers")]
    for name, key in keys:
        say(f"  {name:<28}" + "".join(f"{human(r['breakdown'][key]):>12}" for r in table))
    say(f"  {'TOTAL':<28}" + "".join(f"{human(r['ciphertext']):>12}" for r in table))
    write_csv(os.path.join(args.outdir, "table8_breakdown.csv"),
              ["label", "cpabe", "keyword", "signature", "digests", "headers", "total"],
              [dict(label=r["label"], **r["breakdown"], total=r["ciphertext"]) for r in table])
    say()

    paths = generate_figures(args.outdir)
    say("Figures written")
    say("-" * 66)
    for p in paths:
        say(f"  {p}")

    with open(os.path.join(args.outdir, "summary.txt"), "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
