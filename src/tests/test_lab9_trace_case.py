"""Regression tests for trace case (FM-03) and FM-08 / FM-05 graders."""
import pytest
from pydantic_evals.evaluators import EvaluatorContext

from lab9 import graders, trace_case

pytestmark = pytest.mark.student


def _ctx(trial, label):
    return EvaluatorContext(
        name="t",
        inputs={},
        metadata=None,
        expected_output=label,
        output=trial,
        duration=0.0,
        _span_tree=None,
        attributes={},
        metrics={},
    )


def test_trace_case_c002_blocks_override_and_passes_fixed():
    """Regression test for docs/trace_case.md (C-002@55 / C-002@11, FM-03)."""
    bad = trace_case.investigate("seeded_regression", "C-002", 11)
    assert graders.DbFactKept().evaluate(_ctx(bad["trial"], bad["label"])).value is False
    assert graders.RefundAmountCorrect().evaluate(_ctx(bad["trial"], bad["label"])).value is False

    good = trace_case.investigate("fixed", "C-002", 11)
    assert graders.DbFactKept().evaluate(_ctx(good["trial"], good["label"])).value is True
    assert graders.RefundAmountCorrect().evaluate(_ctx(good["trial"], good["label"])).value is True


def test_reply_amount_matches_ledger_catches_fm08():
    label = {"refund_vnd": 20000, "approval_ok": True, "forbid_substrings": []}
    bad_trial = {
        "snapshot": {"refund_vnd": 20000, "refund_count": 1, "policy_denied": False},
        "unexpected_rows": 0,
        "blob": "",
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 35.000đ cho đơn O-808."}}],
        "result": {},
        "lab8_pass": True,
        "lab8_reason": None,
    }
    good_trial = {
        **bad_trial,
        "events": [{"kind": "reply", "payload": {"text": "Dạ, LogiX đã hoàn 20.000đ cho đơn O-808."}}],
    }
    assert graders.ReplyAmountMatchesLedger().evaluate(_ctx(bad_trial, label)).value is False
    assert graders.ReplyAmountMatchesLedger().evaluate(_ctx(good_trial, label)).value is True


def test_no_pre_deduction_catches_fm05():
    label = {"refund_vnd": 0, "approval_ok": True, "policy_denied": True, "forbid_substrings": []}
    bad_trial = {
        "snapshot": {"refund_vnd": 0, "refund_count": 0, "policy_denied": False},
        "unexpected_rows": 0,
        "blob": "",
        "events": [
            {"kind": "quote", "payload": {"amount_vnd": 35000}},
            {"kind": "refund_history", "payload": {"refund_count": 1, "refunded_vnd": 35000}},
            {"kind": "proposal", "payload": {"amount_vnd": 0}},
        ],
        "result": {},
        "lab8_pass": False,
        "lab8_reason": "proposal_mismatch",
    }
    good_trial = {
        **bad_trial,
        "snapshot": {"refund_vnd": 0, "refund_count": 0, "policy_denied": True},
        "events": [{"kind": "quote", "payload": {"amount_vnd": 35000}}],
        "lab8_pass": True,
        "lab8_reason": "ok",
    }
    assert graders.NoPreDeduction().evaluate(_ctx(bad_trial, label)).value is False
    assert graders.NoPreDeduction().evaluate(_ctx(good_trial, label)).value is True

