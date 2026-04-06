from tests.evals.harness.scorer import score_run


def test_repeatability_score_signal():
    cases = [
        {
            "status": "pass",
            "correctness": 1.0,
            "schema_valid": True,
            "reproducibility_score": 1.0,
            "crash": False,
        },
        {
            "status": "pass",
            "correctness": 0.8,
            "schema_valid": True,
            "reproducibility_score": 0.5,
            "crash": False,
        },
    ]
    result = score_run(cases)
    assert result["weighted_score"] > 0.5
