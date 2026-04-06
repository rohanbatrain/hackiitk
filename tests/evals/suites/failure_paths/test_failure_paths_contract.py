import pytest

from tests.evals.harness.runner import run_eval_case


def test_missing_policy_path_records_error():
    result = run_eval_case(
        case_id="missing-policy",
        policy_path="/home/runner/work/hackiitk/hackiitk/tests/evals/fixtures/clean/does_not_exist.txt",
        model="qwen2.5:3b",
        suite="failure_paths",
        repeat=0,
        domain="isms",
    )
    assert result["status"] == "error"
    assert result["error"]
