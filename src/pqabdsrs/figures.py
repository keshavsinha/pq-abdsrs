"""Regenerates Figures 2 and 3 of the manuscript."""
from __future__ import annotations

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from .params import LEVEL1
from .sizes import ABDSRS_CIPHERTEXT, ABDSRS_PUBLIC_PARAMS, POINTS, SizeModel

plt.rcParams.update({"font.size": 10, "font.family": "serif"})


def figure_public_params(rows, path):
    """Figure 2: public parameter size against |U|, log axis."""
    universes = [r["universe"] for r in rows]
    fig, ax = plt.subplots(figsize=(6.2, 4.0))
    ax.semilogy(universes, [ABDSRS_PUBLIC_PARAMS] * len(rows), "o-",
                color="#1f4e79", label="ABDSRS (pairing-based)")
    ax.semilogy(universes, [r["public_params"] for r in rows], "s-",
                color="#b03a2e", label="PQ-ABDSRS, expanded public matrices")
    ax.semilogy(universes, [r["public_params_seeded"] for r in rows], "^--",
                color="#1e8449", label="PQ-ABDSRS, seed-derived (transmitted)")
    ax.set_xlabel(r"attribute universe size $|U|$")
    ax.set_ylabel("public parameter size (bytes, log scale)")
    ax.set_xticks(universes)
    ax.grid(True, which="both", ls=":", alpha=0.5)
    ax.legend(fontsize=8.5, loc="center right")
    ax.set_title("Public parameter size, complete serialization", fontsize=10)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def figure_ciphertext(rows, path):
    """Figure 3: complete ciphertext by component, against the ABDSRS total."""
    labels = [r["label"] for r in rows]
    x = np.arange(len(rows))
    width = 0.38
    components = [
        ("CP-ABE component", "cpabe", "#1f4e79"),
        ("keyword ciphertext", "keyword", "#2e86c1"),
        ("signature", "signature", "#b03a2e"),
        ("SIS digests", "digests", "#e67e22"),
        ("headers, AEAD, policies", "headers", "#7d3c98"),
    ]
    fig, ax = plt.subplots(figsize=(6.6, 4.0))
    bottom = np.zeros(len(rows))
    for name, key, colour in components:
        values = np.array([r["breakdown"][key] for r in rows], dtype=float)
        ax.bar(x + width / 2, values, width, bottom=bottom, label=name, color=colour)
        bottom += values
    ax.bar(x - width / 2, ABDSRS_CIPHERTEXT[:len(rows)], width,
           label="ABDSRS total", color="#566573")
    ax.set_yscale("log")
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("bytes (log scale), plaintext excluded")
    ax.set_title("Complete serialized ciphertext, component breakdown", fontsize=10)
    ax.legend(fontsize=8, ncol=2)
    ax.grid(True, axis="y", which="both", ls=":", alpha=0.5)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def generate(outdir):
    rows = SizeModel(LEVEL1).table()
    figure_public_params(rows, f"{outdir}/size-params.png")
    figure_ciphertext(rows, f"{outdir}/size-ciphertext.png")
    return [f"{outdir}/size-params.png", f"{outdir}/size-ciphertext.png"]
