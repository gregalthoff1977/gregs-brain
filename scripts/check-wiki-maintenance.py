from pathlib import Path
import os
import sys

workspace = Path(os.environ.get("WORKSPACE_PATH", ".")).resolve()
wiki = workspace / "wiki"
inbox = wiki / "inbox"
overview = wiki / "overview.md"
log = wiki / "log.md"

if not wiki.exists():
    print(f"FAIL: wiki missing: {wiki}")
    sys.exit(1)

if not overview.exists():
    print(f"FAIL: overview.md missing: {overview}")
    sys.exit(1)

if not log.exists():
    print(f"FAIL: log.md missing: {log}")
    sys.exit(1)

inbox_files = list(inbox.glob("*.md")) if inbox.exists() else []

if inbox_files:
    latest_inbox = max(f.stat().st_mtime for f in inbox_files)
    if overview.stat().st_mtime < latest_inbox:
        print("FAIL: overview.md older than latest inbox item")
        sys.exit(1)
    if log.stat().st_mtime < latest_inbox:
        print("FAIL: log.md older than latest inbox item")
        sys.exit(1)

print("PASS: wiki maintenance files are current")
