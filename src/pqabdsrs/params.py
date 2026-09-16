"""
Parameter selection and concrete-hardness estimation for PQ-ABDSRS.

Reproduces Section 9.1 and Table 5 of the manuscript.

Everything here is derived from three stated constraints:
  (C1) TrapGen width          m >= (1 + delta) * n * log2(q),  delta = 1
  (C2) SamplePre Gaussian     sigma >= ||T~|| * omega(sqrt(log 2m))
  (C3) decryption correctness B_dec < q/4

Hardness is reported using the primal-uSVP core-SVP methodology
(Alkim-Ducas-Poppelmann-Schwabe, USENIX Security 2016; Albrecht-Player-Scott,
J. Math. Cryptol. 2015). This is a lower-bound methodology: it does not model
dual or hybrid attacks, and it is NOT a substitute for a full run of the
lattice estimator. See README.md, "Known limitations".
"""

from __future__ import annotations

import math
from dataclasses import dataclass

# BKZ core-SVP cost exponents (sieving).
CLASSICAL_EXP = 0.292
QUANTUM_EXP = 0.265

# Explicit instantiation of omega(sqrt(log n)) in the decryption-error tail bound.
# Any constant above ~sqrt(log2 n) makes the failure probability negligible; 5 is
# the value stated in the manuscript.
OMEGA = 5.0


def root_hermite(b: int) -> float:
    """Root-Hermite factor delta(b) achievable by BKZ with block size b."""
    return ((math.pi * b) ** (1.0 / b) * b / (2 * math.pi * math.e)) ** (1.0 / (2 * (b - 1)))


@dataclass(frozen=True)
class ParameterSet:
    """A complete PQ-ABDSRS parameter set."""

    n: int          # lattice dimension
    log_q: int      # ceil(log2 q)
    s_e: float      # discrete Gaussian parameter of the error distribution chi
    sigma: int      # Gaussian parameter for SamplePre
    kappa: int = 256  # encapsulated key / tag length in bits

    @property
    def q(self) -> int:
        return 2 ** self.log_q

    @property
    def m(self) -> int:
        """Trapdoor matrix width, m = 2 * n * ceil(log2 q)  (constraint C1, delta = 1)."""
        return 2 * self.n * self.log_q

    @property
    def std_e(self) -> float:
        """Standard deviation of chi = D_{Z, s_e}."""
        return self.s_e / math.sqrt(2 * math.pi)

    @property
    def gs_norm(self) -> float:
        """||T~||, the Gram-Schmidt norm of the TrapGen basis, O(sqrt(n log q))."""
        return math.sqrt(self.n * self.log_q)

    def check_sigma(self) -> bool:
        """Constraint C2."""
        return self.sigma >= self.gs_norm * math.sqrt(math.log2(self.m))

    # ---- correctness ------------------------------------------------------

    def key_norm(self) -> float:
        """||e_A|| <= sigma * sqrt(2m)  (Definition 6)."""
        return self.sigma * math.sqrt(2 * self.m)

    def noise_bound(self) -> float:
        """B_dec of Equation (2).

        The clause term is NOT bounded by Cauchy-Schwarz. For e_j drawn from
        D_{Z^{2m}, alpha q} and e_A fixed, <e_A, e_j> is a one-dimensional
        Gaussian of parameter ||e_A|| * alpha q, so

            |<e_A, e_j>| <= ||e_A|| * alpha q * omega(sqrt(log n))

        with overwhelming probability (Gentry-Peikert-Vaikuntanathan, Lemma 2.9).
        Using ||e_A|| * ||e_j|| instead overestimates the error by a factor of
        sqrt(2m), which at these dimensions is more than 400x and pushes an
        otherwise correct parameter set below the q/4 threshold.
        """
        clause = self.key_norm() * self.s_e * OMEGA
        encap = self.s_e * OMEGA * math.sqrt(self.kappa)
        return clause + encap

    def correctness_margin_bits(self) -> float:
        """log2((q/4) / B_dec). Must be > 0 for constraint C3."""
        return math.log2((self.q / 4) / self.noise_bound())

    # ---- concrete hardness ------------------------------------------------

    def lwe_block_size(self, b_max: int = 1400, m_max: int = 8000) -> tuple[int, int]:
        """Smallest BKZ block size solving the primal uSVP instance, and its dimension.

        Success condition (2016 estimate):
            std * sqrt(b) <= delta(b)^(2b - d - 1) * q^((d - n - 1) / d)
        minimized over the number of samples used.
        """
        std = self.std_e
        for b in range(50, b_max):
            delta = root_hermite(b)
            for samples in range(self.n, m_max, 4):
                d = samples + self.n + 1
                if std * math.sqrt(b) <= delta ** (2 * b - d - 1) * self.q ** ((d - self.n - 1) / d):
                    return b, d
        raise ValueError("no block size found below b_max")

    def sis_block_size(self, beta: float, b_max: int = 1400, m_max: int = 12000):
        """Smallest BKZ block size finding a vector of norm <= beta in Lambda^perp.

        Returns None when beta is too small to be reached below b_max, which means
        the instance is at least as hard as block size b_max.
        """
        for b in range(50, b_max):
            delta = root_hermite(b)
            for d in range(self.n, m_max, 8):
                if delta ** d * self.q ** (self.n / d) <= beta:
                    return b, d
        return None

    # ---- SIS norm bounds used by the manuscript ---------------------------

    def beta_signature(self) -> float:
        """beta_s = 2 * sigma * sqrt(2m), the ABS / GPV forgery norm bound."""
        return 2 * self.sigma * math.sqrt(2 * self.m)

    def beta_digest(self) -> float:
        """beta_h = 2 * sqrt(2 n h), the Ajtai-digest collision norm bound (Lemma 1)."""
        return 2 * math.sqrt(2 * self.n * self.log_q)


def core_svp_bits(b: int) -> tuple[float, float]:
    """(classical, quantum) core-SVP cost in bits for block size b."""
    return CLASSICAL_EXP * b, QUANTUM_EXP * b


# The parameter set adopted in Section 9.1 of the manuscript.
LEVEL1 = ParameterSet(n=1536, log_q=30, s_e=8.0, sigma=1024)

# The parameter set used in the pre-revision draft, retained so that the
# manuscript's statement about it can be reproduced rather than taken on trust.
SUPERSEDED_DRAFT = ParameterSet(n=512, log_q=27, s_e=8.0, sigma=512)


def hardness_table(ps: ParameterSet) -> list[dict]:
    """Rows of Table 5."""
    rows = []

    b, d = ps.lwe_block_size()
    c, qm = core_svp_bits(b)
    rows.append(
        dict(instance="LWE_{n,q,chi,m}", beta=None, block_size=b, dim=d,
             classical_bits=c, quantum_bits=qm, exact=True)
    )

    for name, beta in (("SIS_{n,q,2m,beta_s}", ps.beta_signature()),
                       ("SIS_{n,q,2nh,beta_h}", ps.beta_digest())):
        res = ps.sis_block_size(beta)
        if res is None:
            c, qm = core_svp_bits(1400)
            rows.append(dict(instance=name, beta=beta, block_size=None, dim=None,
                             classical_bits=c, quantum_bits=qm, exact=False))
        else:
            b2, d2 = res
            c, qm = core_svp_bits(b2)
            rows.append(dict(instance=name, beta=beta, block_size=b2, dim=d2,
                             classical_bits=c, quantum_bits=qm, exact=True))
    return rows
