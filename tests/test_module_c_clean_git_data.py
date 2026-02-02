import os
import sys


def _ensure_scripts_on_path():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scripts_dir = os.path.join(repo_root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)


_ensure_scripts_on_path()

from module_c.clean_git_data import calculate_scores


def test_calculate_scores_happy_path():
    commits = [
        {"commit": {"message": "feat: add x\n\nbody"}},
        {"commit": {"message": "random message"}},
    ]

    prs = [
        {"body": "this is a detailed pr body"},
        {"labels": [{"name": "bug"}]},
    ]

    runs = [
        {"conclusion": "success"},
        {"conclusion": "failure"},
        {"conclusion": "cancelled"},
    ]

    releases = [
        {"published_at": "2026-02-01T00:00:00Z"},
        {"published_at": "2026-01-01T00:00:00Z"},
    ]

    files_status = {
        ".github/workflows": True,
        "LICENSE": True,
        "README.md": True,
        "CONTRIBUTING.md": False,
        "CODE_OF_CONDUCT.md": False,
        "pom.xml": True,
        ".editorconfig": False,
    }

    data = calculate_scores(
        commits,
        prs,
        runs,
        releases,
        files_status,
        generated_at="2026-02-01 00:00:00",
    )

    assert data["generated_at"] == "2026-02-01 00:00:00"

    assert data["version_control"]["commit_norm"] == 7.5
    assert data["version_control"]["pr_process"] == 10.0
    assert data["version_control"]["total"] == 17.5

    assert data["ci_health"]["run_rate"] == 7.5
    assert data["ci_health"]["config_exist"] == 5
    assert data["ci_health"]["stats"] == "1/2"
    assert data["ci_health"]["total"] == 12.5

    assert data["governance"]["docs"] == 7.5
    assert data["governance"]["release_cycle"] == 15
    assert data["governance"]["total"] == 22.5

    assert data["code_quality"]["test_config"] == 10
    assert data["code_quality"]["style_config"] == 15
    assert data["code_quality"]["total"] == 25

    assert data["total_score"] == 77.5


def test_calculate_scores_release_cycle_penalized_when_slow():
    data = calculate_scores(
        commits=[],
        prs=[],
        runs=[],
        releases=[
            {"published_at": "2026-02-01T00:00:00Z"},
            {"published_at": "2025-07-26T00:00:00Z"},
        ],
        files_status={},
        generated_at="2026-02-01 00:00:00",
    )

    assert data["governance"]["release_cycle"] == 5
