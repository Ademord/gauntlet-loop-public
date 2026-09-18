"""Run the phase-0 ledger end to end: ingest, features, report. Idempotent. Zero model tokens."""
import subprocess
import sys
from pathlib import Path

here = Path(__file__).resolve().parent
for script in ('ingest.py', 'features.py', 'report.py'):
    subprocess.run([sys.executable, str(here / script), *sys.argv[1:]] if script != 'report.py' else [sys.executable, str(here / script)], check=True)
