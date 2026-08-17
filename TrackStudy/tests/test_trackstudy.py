from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


TRACKSTUDY_ROOT = Path(__file__).resolve().parents[1]
SKILL_ROOT = TRACKSTUDY_ROOT / "track-study" / "skills" / "track-study"
SCRIPTS = SKILL_ROOT / "scripts"


def run_script(name: str, *arguments: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPTS / name), *arguments],
        check=check,
        capture_output=True,
        text=True,
    )


class TrackStudyTests(unittest.TestCase):
    def create_study(self, root: Path) -> Path:
        study = root / "study"
        run_script("init_study.py", str(study), "--title", "Test Study")
        return study

    def test_init_build_and_validate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            study = self.create_study(Path(temporary))
            build = run_script("build_atlas.py", str(study))
            self.assertIn("2 experiments, 1 relations", build.stdout)
            validate = run_script("validate_study.py", str(study), "--check-built")
            self.assertIn("validation passed", validate.stdout)
            generated = (study / "web" / "data" / "study.js").read_text(encoding="utf-8")
            self.assertTrue(generated.startswith("window.TRACKSTUDY_DATA = "))
            self.assertIn('"experimentCount": 2', generated)

    def test_init_refuses_to_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            study = self.create_study(Path(temporary))
            result = run_script("init_study.py", str(study), check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("refusing to overwrite", result.stderr)

    def test_stale_evidence_hash_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            study = self.create_study(Path(temporary))
            evidence = study / "evidence" / "method.md"
            evidence.write_text(evidence.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
            result = run_script("validate_study.py", str(study), check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("sourceSha256 is stale", result.stderr)

    def test_primary_cycle_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            study = self.create_study(Path(temporary))
            study_path = study / "study.json"
            payload = json.loads(study_path.read_text(encoding="utf-8"))
            payload["relations"].append(
                {
                    "id": "rel-02-01",
                    "from": "02_gated_method",
                    "to": "01_baseline",
                    "type": "depends_on",
                    "kind": "evolution",
                    "label": "Invalid reverse edge",
                    "primary": True,
                    "evidence": ["ev-method-report"],
                }
            )
            study_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result = run_script("validate_study.py", str(study), check=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("contains a cycle", result.stderr)


if __name__ == "__main__":
    unittest.main()
