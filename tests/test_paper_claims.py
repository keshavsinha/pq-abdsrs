"""
Every assertion here is a number that appears in the manuscript. If one of these
fails, the paper and the code disagree, and the paper is wrong until shown
otherwise. Run with:  pytest -q
"""

import math

import pytest

from pqabdsrs import LEVEL1, SUPERSEDED_DRAFT, core_svp_bits, hardness_table
from pqabdsrs.sizes import POINTS, SizeModel

MB = 1e6
GB = 1e9
KB = 1e3

ps = LEVEL1
model = SizeModel(ps)
rows = model.table()


def approx(value, target, tol=0.01):
    """Within tol relative error."""
    return abs(value - target) / target <= tol


# ---------------------------------------------------------------- Section 9.1

def test_parameter_set():
    assert ps.n == 1536
    assert ps.log_q == 30
    assert ps.m == 92_160
    assert 2 * ps.m == 184_320
    assert ps.sigma == 1024


def test_trapgen_width_constraint():
    """C1: m >= (1 + delta) n log2 q with delta = 1."""
    assert ps.m >= 2 * ps.n * math.log2(ps.q)


def test_sampler_constraint():
    """C2."""
    assert ps.check_sigma()


def test_correctness_margin():
    """C3: the manuscript states B_dec = 2^24.1 against q/4 = 2^28, margin 2^3.9."""
    assert approx(math.log2(ps.noise_bound()), 24.1, tol=0.02)
    assert approx(ps.correctness_margin_bits(), 3.9, tol=0.05)
    assert ps.correctness_margin_bits() > 0


# ------------------------------------------------------------------- Table 5

def test_lwe_hardness_is_level_1():
    b, _ = ps.lwe_block_size()
    classical, quantum = core_svp_bits(b)
    assert b == 563
    assert round(classical) == 164
    assert round(quantum) == 149


def test_sis_instances_are_not_the_bottleneck():
    table = {r["instance"]: r for r in hardness_table(ps)}
    sig = table["SIS_{n,q,2m,beta_s}"]
    assert sig["exact"] is False   # harder than block size 1400
    digest = table["SIS_{n,q,2nh,beta_h}"]
    assert digest["exact"] is False


def test_superseded_draft_was_not_level_1():
    """The manuscript states the old n=512 set gives 2^41 classical, 2^37 quantum."""
    b, _ = SUPERSEDED_DRAFT.lwe_block_size()
    classical, quantum = core_svp_bits(b)
    assert b == 140
    assert round(classical) == 41
    assert round(quantum) == 37


def test_superseded_draft_matrix_width_was_wrong():
    """5 n log2 q = 69,120, not the ~6,900 the draft stated."""
    assert 5 * SUPERSEDED_DRAFT.n * SUPERSEDED_DRAFT.log_q == 69_120


# ------------------------------------------------------------------- Table 7

@pytest.mark.parametrize("index,expected_gb", [(0, 54.68), (1, 107.76), (2, 160.85), (3, 213.93)])
def test_public_parameters(index, expected_gb):
    assert approx(rows[index]["public_params"] / GB, expected_gb)


def test_public_parameter_gap_exceeds_six_orders():
    for row in rows:
        assert row["public_params_ratio"] > 1e7


@pytest.mark.parametrize("index,expected_kb", [(0, 3.33), (1, 6.53), (2, 9.73), (3, 12.93)])
def test_seeded_public_parameters(index, expected_kb):
    assert approx(rows[index]["public_params_seeded"] / KB, expected_kb, tol=0.02)


def test_decryption_key_is_a_matrix_not_a_vector():
    """A1: a single preimage vector leaks K_i XOR K_j. The key is 2m x kappa."""
    sizes = {row["decryption_key"] for row in rows}
    assert len(sizes) == 1
    assert approx(rows[0]["decryption_key"] / MB, 82.58)
    assert rows[0]["decryption_key"] == model.vec_gaussian(2 * ps.m) * ps.kappa


@pytest.mark.parametrize("index,expected_mb", [(0, 21.44), (1, 42.21), (2, 62.98), (3, 83.75)])
def test_ciphertext_totals(index, expected_mb):
    assert approx(rows[index]["ciphertext"] / MB, expected_mb)


@pytest.mark.parametrize("index,expected_ratio", [(0, 2829), (1, 3526), (2, 3846), (3, 4031)])
def test_ciphertext_ratio_against_abdsrs(index, expected_ratio):
    assert approx(rows[index]["ciphertext_ratio"], expected_ratio, tol=0.02)


def test_pq_ciphertext_is_larger_not_smaller():
    """The pre-revision draft claimed the opposite. It was an artefact of omissions."""
    for row in rows:
        assert row["ciphertext_ratio"] > 2000


# ------------------------------------------------------------------- Table 8

def test_breakdown_sums_to_total():
    for row in rows:
        assert approx(sum(row["breakdown"].values()), row["ciphertext"], tol=1e-9)


def test_every_ciphertext_component_is_counted():
    """Guards against the omission the reviewer identified."""
    expected = {"cpabe", "keyword", "signature", "digests", "headers"}
    assert set(rows[0]["breakdown"]) == expected


@pytest.mark.parametrize("index,expected_mb", [(0, 3.461), (1, 6.922), (2, 10.382), (3, 13.843)])
def test_cpabe_component(index, expected_mb):
    assert approx(rows[index]["breakdown"]["cpabe"] / MB, expected_mb)


@pytest.mark.parametrize("index,expected_mb", [(0, 17.63), (1, 34.91), (2, 52.19), (3, 69.47)])
def test_keyword_component(index, expected_mb):
    assert approx(rows[index]["breakdown"]["keyword"] / MB, expected_mb)


def test_signature_component_constant():
    for row in rows:
        assert approx(row["breakdown"]["signature"] / KB, 322.6)


# ---------------------------------------------------------------- unit sizes

def test_unit_sizes_quoted_in_section_9_3():
    assert model.vec_zq(ps.n) == 5_760
    assert model.vec_zq(ps.m) == 345_600
    assert model.vec_zq(2 * ps.m) == 691_200
    assert approx(model.public_matrix() / MB, 530.84)
    assert model.vec_gaussian(2 * ps.m) == 322_560
    assert model.gaussian_coord_bits == 14


def test_parameter_points_match_the_manuscript():
    assert [(p.label, p.universe, p.clauses, p.keywords) for p in POINTS] == [
        ("ip-1", 50, 5, 4), ("ip-2", 100, 10, 6),
        ("ip-3", 150, 15, 8), ("ip-4", 200, 20, 10)]


# ------------------------------------------------- regression, found by this suite

def test_noise_bound_uses_the_gaussian_tail_not_cauchy_schwarz():
    """The pre-revision draft evaluated B_dec incorrectly.

    Cauchy-Schwarz gives ||e_A|| * ||e_j||, which is larger than the correct
    Gaussian tail bound by a factor of order sqrt(2m) * std / (s_e * omega).
    At these dimensions that is about 34x, roughly five bits of modulus, and it
    is the difference between a parameter set that satisfies q/4 > B_dec and one
    that does not.
    """
    cauchy_schwarz = ps.key_norm() * ps.std_e * math.sqrt(2 * ps.m)
    assert 30 < cauchy_schwarz / ps.noise_bound() < 40
    assert math.log2(cauchy_schwarz) > ps.log_q - 2   # would violate C3
    assert math.log2(ps.noise_bound()) < ps.log_q - 2  # the correct bound does not


# ------------------------------------------- regressions from the A1-A3 audit

def test_keyword_ciphertext_scales_with_universe_not_keyword_count():
    """A3: the LWE KP-ABE ciphertext carries one component per attribute POSITION.

    An earlier draft modelled it as (|W| + 1) components, which would have made
    it independent of |U^circ|. BGG+14's short-ciphertext variant needs
    multilinear maps and is not available under LWE.
    """
    m0 = SizeModel(ps)
    a = m0.keyword_ciphertext(50)
    b = m0.keyword_ciphertext(200)
    assert b > 3 * a
    # and the reported figure must use the universe, not the keyword count
    for row, pt in zip(rows, POINTS):
        assert row["breakdown"]["keyword"] == m0.keyword_ciphertext(pt.universe)


def test_keyword_trapdoor_is_constant():
    """A3: BGG+14 has short secret keys; the trapdoor does not grow with the policy."""
    assert len({row["keyword_trapdoor"] for row in rows}) == 1
    assert approx(rows[0]["keyword_trapdoor"] / KB, 322.6)


def test_keyword_ciphertext_dominates_the_total():
    """The consequence of A3: the keyword layer, not the access-control layer,
    is now the largest ciphertext component at every parameter point."""
    for row in rows:
        b = row["breakdown"]
        assert b["keyword"] == max(b.values())
        assert b["keyword"] > b["cpabe"]
