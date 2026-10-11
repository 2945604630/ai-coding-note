"""Direct-file launcher usable from any working directory."""
from pathlib import Path
import sys

if __package__ in (None, ''):
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from experiments.feature_validation.F03_evidence_verification.__main__ import main

if __name__ == '__main__':
    raise SystemExit(main())
