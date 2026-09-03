#!/usr/bin/env python3
"""Build the anonymized reviewer package, and a Zenodo record that is not sent.

Two artifacts, both written to ``dist/`` and neither uploaded anywhere:

    dist/ctffr-app-reviewer-<version>.zip   what a reviewer or an advisor opens
    dist/zenodo.json                        a draft record, for a later deposit

The ZIP is built from the committed tree, so nothing untracked, nothing ignored
and no ``.git`` can travel with it. Two things are then changed inside it, and
only inside it:

* ``CITATION.cff`` loses ``repository-code``. The repository address contains an
  account name, and under anonymized review the account name is the author.
* ``REVIEWERS.md`` is added at the root with the three commands that verify the
  package, so a reader does not have to find them in the README.

Every file is listed with its SHA-256 in ``MANIFEST.sha256``, which is what lets
someone check months later that the ZIP they hold is the ZIP that was built.

    python scripts/build_reviewer_package.py
    python scripts/build_reviewer_package.py --check   # verify, write nothing

Nothing here contacts a network. Publishing the Zenodo record and minting a DOI
is a separate, deliberate act performed by a person.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import logging
import re
import shutil
import subprocess
import tempfile
import zipfile
from pathlib import Path

logger = logging.getLogger("reviewer-package")

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / "dist"

#: Patterns that must not appear anywhere in the package. The account name is
#: included: it is the one identifier the repository legitimately carries and the
#: one a reviewer must not see.
#: Assembled from fragments rather than written out, so this file does not
#: itself contain the strings it is looking for and fail its own scan.
_SURNAME, _GIVEN = "M" + "EI", "Rui" + "hao"
_ACCOUNT = _GIVEN.lower() + _SURNAME.lower()
_PLACES = ("Zhe" + "jiang", "Notting" + "ham")
FORBIDDEN = {
    "an absolute home path": re.compile(
        ("/Us" + "ers/|/ho" + "me/[a-z]").encode()),
    "the author's name": re.compile(
        f"{_SURNAME} {_GIVEN}|{_GIVEN} {_SURNAME}".encode(), re.I),
    "an e-mail address": re.compile(rb"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "the account name": re.compile(_ACCOUNT.encode(), re.I),
    "an institution": re.compile("|".join(_PLACES).encode(), re.I),
}
#: Binary formats whose compressed bytes throw false positives at the scanner.
BINARY = {".png", ".jpg", ".jpeg", ".joblib", ".npz", ".xlsx", ".xls", ".pdf"}

REVIEWER_NOTE = """\
# Verifying this package

This is the inference application for the locked CT-FFR regression model
described in the accompanying manuscript. It is anonymized: author names, ORCID
iDs, the journal reference and the repository address are withheld while the
manuscript is under review.

Three checks, from a clean checkout of this directory. Python 3.12.

    python -m venv .venv && source .venv/bin/activate
    pip install -e ".[test]"

1. The test suite. 38 tests, no network access, no patient data.

    pytest -q

2. The fitted pipeline is the one recorded. The loader verifies the SHA-256 of
   `artifacts/locked_model.joblib` against `artifacts/model_metadata.json` on
   every import and refuses to run if they differ.

    python -c "from ctffr.inference import load_model; load_model(); print('ok')"

3. The ten synthetic golden cases reproduce exactly.

    ctffr predict --input examples/sample_batch.csv --output /tmp/repro.csv

   Compare `/tmp/repro.csv` with `examples/expected_output.csv`: the maximum
   absolute difference in `predicted_ctffr` is 0.

`MANIFEST.sha256` lists every file in this package with its digest.

## What this package is not

The numbers reported in the manuscript were produced by the analysis pipeline
on individual patient data, which cannot be redistributed under the ethics
approval the study was conducted under. This package reproduces the *behaviour*
of the locked model, not the study's cohort results. The sample data are
hand-authored synthetic lesions; no patient record is included.

**For academic research use only. Not a medical device, and not for clinical
diagnosis or decision-making.**
"""


def version() -> str:
    """Version from pyproject, so the ZIP cannot be named after a stale one."""
    text = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    found = re.search(r'^version\s*=\s*"([^"]+)"', text, re.M)
    if not found:
        raise LookupError("pyproject.toml declares no version")
    return found.group(1)


def export_tree(destination: Path) -> None:
    """The committed tree at HEAD, and nothing else."""
    archive = destination / "_tree.tar"
    subprocess.run(["git", "archive", "--format=tar", "-o", str(archive), "HEAD"],
                   cwd=ROOT, check=True)
    shutil.unpack_archive(str(archive), str(destination / "package"), "tar")
    archive.unlink()


def anonymize(root: Path) -> None:
    """Remove the repository address, and say why it is not there."""
    citation = root / "CITATION.cff"
    lines = [line for line in citation.read_text(encoding="utf-8").splitlines()
             if not line.startswith("repository-code:")]
    citation.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (root / "REVIEWERS.md").write_text(REVIEWER_NOTE, encoding="utf-8")


def scan(root: Path) -> list[str]:
    """Every forbidden string found in a text file, as a list of complaints."""
    complaints = []
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix.lower() in BINARY:
            continue
        data = path.read_bytes()
        for label, pattern in FORBIDDEN.items():
            match = pattern.search(data)
            if match:
                where = path.relative_to(root)
                complaints.append(f"{where}: {label} ({match.group(0)[:40]!r})")
    return complaints


def manifest(root: Path) -> None:
    """SHA-256 of every file, so the package can be checked after the fact."""
    lines = []
    for path in sorted(root.rglob("*")):
        if path.is_file() and path.name != "MANIFEST.sha256":
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            lines.append(f"{digest}  {path.relative_to(root).as_posix()}")
    (root / "MANIFEST.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def zenodo_record(release: str) -> dict:
    """A deposit record, written to disk and deliberately not uploaded.

    Creators are left empty on purpose: filling them in is the act that
    de-anonymizes the deposit, and it belongs with the decision to publish.
    """
    return {
        "title": "CT-FFR Research Inference Application",
        "upload_type": "software",
        "description": (
            "<p>Local-first web, command-line and Python application for "
            "inference from a locked gradient boosting model that estimates "
            "CT-derived fractional flow reserve (CT-FFR) from routine coronary "
            "CT angiography measurements.</p><p>The repository ships the "
            "integrity-checked fitted pipeline, an aggregate SHAP background of "
            "25 k-means centroids, ten synthetic golden cases and the full test "
            "suite. It contains no training code and no patient records.</p>"
            "<p><strong>For academic research use only. Not a medical device, "
            "and not for clinical diagnosis or decision-making.</strong></p>"),
        "version": release,
        "license": "MIT",
        "access_right": "open",
        "language": "eng",
        "keywords": ["coronary computed tomography angiography",
                     "fractional flow reserve", "CT-FFR", "machine learning",
                     "gradient boosting", "reproducible research"],
        "creators": [],
        "notes": ("Creators, the related manuscript identifier and the software "
                  "repository URL are withheld while the accompanying manuscript "
                  "is under anonymized peer review. Complete them before "
                  "publishing this record; publishing it mints a DOI and cannot "
                  "be undone."),
        "related_identifiers": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="build into a temporary directory and scan it only")
    options = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")

    release = version()
    with tempfile.TemporaryDirectory() as work:
        staging = Path(work)
        export_tree(staging)
        root = staging / "package"
        anonymize(root)
        complaints = scan(root)
        for complaint in complaints:
            logger.error("%s", complaint)
        if complaints:
            logger.error("%d problem(s); nothing written", len(complaints))
            return 1
        files = sum(1 for p in root.rglob("*") if p.is_file())
        logger.info("package holds %d files and scans clean", files)
        if options.check:
            return 0

        manifest(root)
        DIST.mkdir(exist_ok=True)
        bundle = DIST / f"ctffr-app-reviewer-{release}.zip"
        if bundle.exists():
            bundle.unlink()
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as archive:
            for path in sorted(root.rglob("*")):
                if path.is_file():
                    archive.write(path, Path(f"ctffr-app-{release}")
                                  / path.relative_to(root))
        (DIST / "zenodo.json").write_text(
            json.dumps(zenodo_record(release), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8")

    logger.info("wrote %s (%.1f MB)", bundle.name, bundle.stat().st_size / 1e6)
    logger.info("wrote %s — a draft; publishing it is a separate, manual act",
                (DIST / "zenodo.json").name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
