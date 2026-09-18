"""commit-msg guard (backlog B-003): a commit that changes skill/ must name the upgrade run that accepted the change.

CONTRIBUTING.md says nobody edits skill/ directly; changes arrive only through an upgrade run with frozen checks and
independent critics. This hook makes that mechanical: if any staged path is under skill/, the commit message must
contain a line `Upgrade-run: <run-id>` whose run folder gauntlet/<run-id>/ exists in the index or the working tree.
Zero model tokens. Installed with the other hooks: git config core.hooksPath tools/hooks
"""
import re
import subprocess
import sys
from pathlib import Path

repo = Path(__file__).resolve().parents[2]
msg_file = Path(sys.argv[1])
staged = subprocess.run(['git', 'diff', '--cached', '--name-only'], cwd=repo, capture_output=True, text=True).stdout.split()
if not any(p == 'skill' or p.startswith('skill/') for p in staged):
    sys.exit(0)
message = msg_file.read_text(encoding='utf-8', errors='replace')
m = re.search(r'^Upgrade-run:\s*(\S+)\s*$', message, re.M)
if not m:
    print('COMMIT REFUSED: this commit changes skill/ but its message has no "Upgrade-run: <run-id>" line.\n'
          'Skill changes land only through an upgrade run (see CONTRIBUTING.md and versions/README.md).', file=sys.stderr)
    sys.exit(1)
run_id = m.group(1)
indexed = subprocess.run(['git', 'ls-files', f'gauntlet/{run_id}/'], cwd=repo, capture_output=True, text=True).stdout.strip()
if not indexed and not (repo / 'gauntlet' / run_id).is_dir():
    print(f'COMMIT REFUSED: Upgrade-run names gauntlet/{run_id}/, which does not exist.', file=sys.stderr)
    sys.exit(1)
print(f'check_commit_msg: skill/ change tied to upgrade run {run_id}')
