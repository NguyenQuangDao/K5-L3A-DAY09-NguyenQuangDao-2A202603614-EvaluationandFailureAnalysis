"""Extra Advanced/Expert tests for M6 pass_hat_k validation and M7 hidden anti-gaming traps."""
import copy
import pytest

from lab9 import gate, stats

pytestmark = pytest.mark.student

ROWS = [
    {"item_id": f"E-{i:03d}", "seed": s, "pass_rate": True, "slices": ["money_movement"] if i < 2 else []}
    for i in range(4)
    for s in (1, 2)
]
SPEC = {
    "eval_set_version": "v2",
    "metrics": [{"id": "pass_rate", "kind": "capability", "blocking": True, "threshold": {"min": 0.8}}],
    "slices": [{"name": "money_movement", "metric": "pass_rate", "min": 0.9, "no_significant_drop": True, "blocking": True}],
}


def _report(rows, metrics=None, failures=None):
    return {
        "manifest": {"eval_set_sha": "x", "items": 4, "seeds": [1, 2]},
        "rows": rows,
        "metrics": metrics or {"pass_rate": 1.0},
        "evaluator_failures": failures or [],
    }


def test_pass_hat_k_rejects_bad_args():
    for args in [(5, 6, 1), (5, 2, 0), (3, 1, 4), (5, -1, 1)]:
        with pytest.raises(ValueError):
            stats.pass_hat_k(*args)


def test_integrity_blocks_duplicate_rows_and_evaluator_failures():
    base = _report(copy.deepcopy(ROWS))
    dup = _report(copy.deepcopy(ROWS[:-1]) + [copy.deepcopy(ROWS[0])])
    assert gate.integrity_check(dup, base, SPEC, SPEC)

    ef = _report(copy.deepcopy(ROWS), failures=["E-001@1:Grader:crash"])
    assert gate.integrity_check(ef, base, SPEC, SPEC)


def test_integrity_blocks_slice_relabeling_and_ratchet_slice_removal():
    base = _report(copy.deepcopy(ROWS))
    relabeled = copy.deepcopy(ROWS)
    relabeled[0]["slices"] = []
    assert gate.integrity_check(_report(relabeled), base, SPEC, SPEC)

    loose = copy.deepcopy(SPEC)
    loose["slices"][0].pop("no_significant_drop")
    assert gate.integrity_check(base, base, loose, SPEC)

