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


@pytest.mark.parametrize("index,expected_kb", [(0, 9.1), (1, 12.3), (2, 15.5), (3, 18.7)])
def test_seeded_public_parameters(index, expected_kb):
    assert approx(rows[index]["public_params_seeded"] / KB, expected_kb, tol=0.02)


def test_decryption_key_is_constant_and_322_6_kb():
    sizes = {row["decryption_key"] for row in rows}
    assert len(sizes) == 1
    assert approx(rows[0]["decryption_key"] / KB, 322.6)


@pytest.mark.parametrize("index,expected_mb", [(0, 5.54), (1, 9.71), (2, 13.89), (3, 18.07)])
def test_ciphertext_totals(index, expected_mb):
    assert approx(rows[index]["ciphertext"] / MB, expected_mb)


@pytest.mark.parametrize("index,expected_ratio", [(0, 731), (1, 811), (2, 848), (3, 870)])
def test_ciphertext_ratio_against_abdsrs(index, expected_ratio):
    assert approx(rows[index]["ciphertext_ratio"], expected_ratio, tol=0.02)


def test_pq_ciphertext_is_larger_not_smaller():
    """The pre-revision draft claimed the opposite. It was an artefact of omissions."""
    for row in rows:
        assert row["ciphertext_ratio"] > 500


# ------------------------------------------------------------------- Table 8

def test_breakdown_sums_to_total():
    for row in rows:
        assert approx(sum(row["breakdown"].values()), row["ciphertext"], tol=1e-9)


def test_every_ciphertext_component_is_counted():
    """Guards against the omission the reviewer identified."""
    expected = {"cpabe", "keyword", "signature", "digests", "headers"}
    assert set(rows[0]["breakdown"]) == expected


@pytest.mark.parametrize("index,expected_mb", [(0, 3.456), (1, 6.913), (2, 10.369), (3, 13.825)])
def test_cpabe_component(index, expected_mb):
    assert approx(rows[index]["breakdown"]["cpabe"] / MB, expected_mb)


@pytest.mark.parametrize("index,expected_mb", [(0, 1.728), (1, 2.420), (2, 3.111), (3, 3.802)])
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
