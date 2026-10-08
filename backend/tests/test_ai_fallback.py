import pytest

from app.ai.classifier import _parse
from app.ai.fallback import rule_classify
from app.services.royalty_service import next_payout_date
from datetime import date


def test_rule_classify_royalty():
    cat, pri = rule_classify("No royalty", "I have not received any royalty for 6 months")
    assert cat == "Royalty & Payments" and pri in ("High", "Critical")


def test_rule_classify_low_priority():
    cat, pri = rule_classify("Update bio", "Can I change my author bio?")
    assert pri == "Low"


def test_parse_rejects_bad_ai_output():
    with pytest.raises(ValueError):
        _parse('{"category": "Made Up", "priority": "High"}')


def test_next_payout_date():
    assert next_payout_date(date(2026, 10, 7)) == date(2026, 11, 14)  # Sep 30 + 45 days