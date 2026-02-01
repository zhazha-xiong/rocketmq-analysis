import os
import sys

import pandas as pd
from module_b.clean_git_data import clean_commits_csv

def test_clean_commits_csv_filters_merge_and_shifts_timezone(tmp_path):
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    scripts_dir = os.path.join(repo_root, "scripts")
    if scripts_dir not in sys.path:
        sys.path.insert(0, scripts_dir)


    commits_csv = tmp_path / "commits.csv"
    out_csv = tmp_path / "clean_commits.csv"

    df = pd.DataFrame(
        [
            {
                "authored_utc": "2026-02-01T00:00:00Z",
                "author_name": "alice",
                "subject": "feat: add x",
            },
            {
                "authored_utc": "2026-02-01T01:00:00Z",
                "author_name": "bob",
                "subject": "Merge pull request #123 from foo/bar",
            },
        ]
    )
    df.to_csv(commits_csv, index=False)

    clean_commits_csv(str(commits_csv), str(out_csv))

    out_df = pd.read_csv(out_csv)

    assert len(out_df) == 1
    assert out_df.loc[0, "name"] == "alice"

    assert out_df.loc[0, "time"].startswith("2026-02-01 08:00")
