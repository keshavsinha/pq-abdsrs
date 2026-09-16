"""
Complete serialized-size accounting for PQ-ABDSRS.

Reproduces Tables 7 and 8 of the manuscript. Every object named in
Algorithms 1-9 is counted here; the point of this module is that the totals
cannot be produced without listing every component, which is the failure mode
the reviewer identified in the pre-revision draft.

Convention, matching Table 4 of Bera et al. (2023): plaintext bytes are
excluded from every ciphertext figure.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field

from .params import ParameterSet

# ABDSRS reported figures, Fig. 4 of Bera et al., J. Inf. Secur. Appl. 75:103482.
ABDSRS_PUBLIC_PARAMS = 2176                          # bytes, constant in |U|
ABDSRS_DECRYPTION_KEY = (1536, 2816, 4096, 5376)     # bytes, at ip-1 .. ip-4
ABDSRS_CIPHERTEXT = (7579, 11971, 16373, 20775)      # bytes, plaintext excluded

SEED_BYTES = 32       # public seed for matrix derivation (Remark 2)
AEAD_NONCE = 12       # 96-bit nonce
AEAD_TAG = 16         # 128-bit tag
TAG_BYTES = 32        # H_5 output, kappa = 256 bits
ATTR_INDEX_BYTES = 2  # one attribute index inside a policy description
CLAUSE_WIDTH = 5      # attributes per DNF clause assumed in the size model
NAME_BYTES = 16       # one keyword generic name


@dataclass(frozen=True)
class ParameterPoint:
    """One column of Table 7."""

    label: str
    universe: int     # |U|, and |U^circ| = |U|
    clauses: int      # ell_e, number of DNF clauses
    keywords: int     # varsigma = |W|


POINTS = (
    ParameterPoint("ip-1", 50, 5, 4),
    ParameterPoint("ip-2", 100, 10, 6),
    ParameterPoint("ip-3", 150, 15, 8),
    ParameterPoint("ip-4", 200, 20, 10),
)


class SizeModel:
    """Byte sizes of every serialized object, for a given parameter set."""

    def __init__(self, ps: ParameterSet):
        self.ps = ps

    # ---- unit sizes -------------------------------------------------------

    @property
    def zq_bits(self) -> int:
        return self.ps.log_q

    def vec_zq(self, dim: int) -> float:
        """A vector in Z_q^dim."""
        return dim * self.zq_bits / 8

    def matrix_zq(self, rows: int, cols: int) -> float:
        return rows * cols * self.zq_bits / 8

    @property
    def gaussian_coord_bits(self) -> int:
        """Bits per coordinate of a discrete Gaussian vector, tail cut at 6 sigma."""
        return math.ceil(math.log2(2 * 6 * self.ps.sigma + 1))

    def vec_gaussian(self, dim: int) -> float:
        return dim * self.gaussian_coord_bits / 8

    # ---- named objects ----------------------------------------------------

    def public_matrix(self) -> float:
        """One matrix in Z_q^{n x m}."""
        return self.matrix_zq(self.ps.n, self.ps.m)

    def n_public_matrices(self, universe: int) -> int:
        """A_0, {A_x}_{x in U}, A_h, plus the keyword layer's |U^circ| + 1.

        A_h lives in Z_q^{n x 2nh}, and 2nh = m, so it costs one matrix.
        The ABS public parameters of El Kaafarani-Katsumata are additional and
        are deliberately NOT counted, so these figures are lower bounds.
        """
        return (universe + 2) + (universe + 1)

    def public_params_expanded(self, universe: int) -> float:
        return (self.n_public_matrices(universe) * self.public_matrix()
                + self.vec_zq(self.ps.n)                 # u
                + self.vec_zq(self.ps.kappa))            # misc

    def public_params_seeded(self, universe: int) -> float:
        """Remark 2: transmitted size only. Working memory is unchanged."""
        return self.n_public_matrices(universe) * SEED_BYTES + self.vec_zq(self.ps.n)

    def decryption_key(self) -> float:
        """One Gaussian vector in Z^{2m}; independent of |A_d|."""
        return self.vec_gaussian(2 * self.ps.m)

    def signature(self) -> float:
        """GPV lower bound on the ABS signature size."""
        return self.vec_gaussian(2 * self.ps.m)

    def cpabe_component(self, clauses: int) -> float:
        """{c_j} in Z_q^{2m} per clause, plus c_u in Z_q^kappa."""
        return clauses * self.vec_zq(2 * self.ps.m) + self.vec_zq(self.ps.kappa)

    def digests(self, clauses: int) -> float:
        """{d_j} in Z_q^n, one per clause."""
        return clauses * self.vec_zq(self.ps.n)

    def keyword_ciphertext(self, keywords: int) -> float:
        """KP-ABE ciphertext: (varsigma + 1) vectors in Z_q^m plus the payload."""
        return (keywords + 1) * self.vec_zq(self.ps.m) + self.vec_zq(self.ps.kappa)

    def keyword_trapdoor(self, keywords: int) -> float:
        """KP-ABE key: one short vector in Z^m per formula leaf."""
        return keywords * self.vec_gaussian(self.ps.m)

    def headers(self, clauses: int, keywords: int) -> float:
        """Policy descriptions, generic names, tag, nonce, AEAD tag."""
        policy = clauses * CLAUSE_WIDTH * ATTR_INDEX_BYTES
        return 2 * policy + keywords * NAME_BYTES + TAG_BYTES + AEAD_NONCE + AEAD_TAG

    # ---- composite --------------------------------------------------------

    def ciphertext_breakdown(self, pt: ParameterPoint) -> dict[str, float]:
        """Table 8."""
        return {
            "cpabe": self.cpabe_component(pt.clauses),
            "keyword": self.keyword_ciphertext(pt.keywords),
            "signature": self.signature(),
            "digests": self.digests(pt.clauses),
            "headers": self.headers(pt.clauses, pt.keywords),
        }

    def ciphertext(self, pt: ParameterPoint) -> float:
        return sum(self.ciphertext_breakdown(pt).values())

    def transformed_ciphertext(self, pt: ParameterPoint) -> float:
        """CT_out carries c_out, c_u, tau', the full digest list, policies and the
        signature, because signature verification at the DU needs all of them."""
        return (self.vec_zq(2 * self.ps.m)
                + self.vec_zq(self.ps.kappa)
                + self.signature()
                + self.digests(pt.clauses)
                + self.headers(pt.clauses, pt.keywords))

    def row(self, pt: ParameterPoint, index: int) -> dict:
        ct = self.ciphertext(pt)
        pp = self.public_params_expanded(pt.universe)
        dk = self.decryption_key()
        return dict(
            label=pt.label,
            universe=pt.universe,
            clauses=pt.clauses,
            keywords=pt.keywords,
            public_params=pp,
            public_params_seeded=self.public_params_seeded(pt.universe),
            public_params_ratio=pp / ABDSRS_PUBLIC_PARAMS,
            decryption_key=dk,
            decryption_key_ratio=dk / ABDSRS_DECRYPTION_KEY[index],
            ciphertext=ct,
            ciphertext_ratio=ct / ABDSRS_CIPHERTEXT[index],
            keyword_trapdoor=self.keyword_trapdoor(pt.keywords),
            transformed_ciphertext=self.transformed_ciphertext(pt),
            breakdown=self.ciphertext_breakdown(pt),
        )

    def table(self) -> list[dict]:
        return [self.row(pt, i) for i, pt in enumerate(POINTS)]


def human(nbytes: float) -> str:
    """Decimal units, as used in the manuscript."""
    for unit, scale in (("GB", 1e9), ("MB", 1e6), ("KB", 1e3)):
        if nbytes >= scale:
            return f"{nbytes / scale:.2f} {unit}"
    return f"{nbytes:,.0f} B"
