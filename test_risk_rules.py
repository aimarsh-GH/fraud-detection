from risk_rules import label_risk, score_transaction


def test_label_risk_thresholds():
    assert label_risk(10) == "low"
    assert label_risk(35) == "medium"
    assert label_risk(75) == "high"


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


def test_high_device_risk_score_increases_risk():
    baseline = score_transaction(_base_tx())
    risky = score_transaction(_base_tx(device_risk_score=80))
    assert risky > baseline


def test_international_transaction_increases_risk():
    baseline = score_transaction(_base_tx())
    international = score_transaction(_base_tx(is_international=1))
    assert international > baseline


def test_high_velocity_increases_risk():
    baseline = score_transaction(_base_tx())
    high_velocity = score_transaction(_base_tx(velocity_24h=8))
    assert high_velocity > baseline


def test_prior_chargebacks_increase_risk():
    baseline = score_transaction(_base_tx())
    repeat_offender = score_transaction(_base_tx(prior_chargebacks=3))
    assert repeat_offender > baseline
