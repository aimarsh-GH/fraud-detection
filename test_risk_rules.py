import pytest

from risk_rules import label_risk, score_transaction


def test_label_risk_thresholds():
    assert label_risk(10) == "low"
    assert label_risk(35) == "medium"
    assert label_risk(75) == "high"


@pytest.mark.parametrize(
    "score, expected_label",
    [
        (29, "low"),
        (30, "medium"),
        (59, "medium"),
        (60, "high"),
    ],
)
def test_label_risk_boundary_values(score, expected_label):
    assert label_risk(score) == expected_label


def test_large_amount_adds_risk():
    tx = {
        "device_risk_score": 10,
        "is_international": 0,
        "amount_usd": 1200,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
    }
    assert score_transaction(tx) >= 25


def _base_tx(**overrides):
    """All fields at their lowest-risk value; score_transaction should return 0."""
    tx = {
        "device_risk_score": 10,
        "is_international": 0,
        "amount_usd": 50,
        "velocity_24h": 1,
        "failed_logins_24h": 0,
        "prior_chargebacks": 0,
    }
    tx.update(overrides)
    return tx


def test_baseline_transaction_scores_zero():
    assert score_transaction(_base_tx()) == 0


@pytest.mark.parametrize(
    "device_risk_score, expected_points",
    [
        (39, 0),
        (40, 10),
        (69, 10),
        (70, 25),
    ],
)
def test_device_risk_score_thresholds(device_risk_score, expected_points):
    tx = _base_tx(device_risk_score=device_risk_score)
    assert score_transaction(tx) == expected_points


@pytest.mark.parametrize(
    "is_international, expected_points",
    [
        (0, 0),
        (1, 15),
    ],
)
def test_international_transaction_thresholds(is_international, expected_points):
    tx = _base_tx(is_international=is_international)
    assert score_transaction(tx) == expected_points


@pytest.mark.parametrize(
    "amount_usd, expected_points",
    [
        (499, 0),
        (500, 10),
        (999, 10),
        (1000, 25),
    ],
)
def test_amount_thresholds(amount_usd, expected_points):
    tx = _base_tx(amount_usd=amount_usd)
    assert score_transaction(tx) == expected_points


@pytest.mark.parametrize(
    "velocity_24h, expected_points",
    [
        (2, 0),
        (3, 5),
        (5, 5),
        (6, 20),
    ],
)
def test_velocity_thresholds(velocity_24h, expected_points):
    tx = _base_tx(velocity_24h=velocity_24h)
    assert score_transaction(tx) == expected_points


@pytest.mark.parametrize(
    "failed_logins_24h, expected_points",
    [
        (1, 0),
        (2, 10),
        (4, 10),
        (5, 20),
    ],
)
def test_failed_logins_thresholds(failed_logins_24h, expected_points):
    tx = _base_tx(failed_logins_24h=failed_logins_24h)
    assert score_transaction(tx) == expected_points


@pytest.mark.parametrize(
    "prior_chargebacks, expected_points",
    [
        (0, 0),
        (1, 5),
        (2, 20),
        (3, 20),
    ],
)
def test_prior_chargebacks_thresholds(prior_chargebacks, expected_points):
    tx = _base_tx(prior_chargebacks=prior_chargebacks)
    assert score_transaction(tx) == expected_points


def test_score_is_capped_at_100_for_worst_case_transaction():
    tx = _base_tx(
        device_risk_score=95,
        is_international=1,
        amount_usd=5000,
        velocity_24h=12,
        failed_logins_24h=8,
        prior_chargebacks=4,
    )
    assert score_transaction(tx) == 100
