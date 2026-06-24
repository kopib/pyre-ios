"""Environment setup and validation for the headless iOS job runner."""

import importlib
import logging
import sys
from pathlib import Path
from typing import Final

from utils.logger import setup_standalone_logging

logger = logging.getLogger(__name__)

# Minimum Python version required by the job scripts
MIN_PYTHON: Final[tuple[int, int]] = (3, 11)

# Third-party packages that job scripts depend on
REQUIRED_PACKAGES: Final[list[tuple[str, str]]] = [
    ("bs4", "beautifulsoup4"),
    ("curl_cffi", "curl-cffi"),
    ("requests", "requests"),
]

# Job scripts that must be present alongside this setup script
EXPECTED_JOBS: Final[list[str]] = [
    "finanzen_net.py",
]


def _check_python_version() -> bool:
    """Verifies the running Python version meets the minimum requirement."""
    current = sys.version_info[:2]
    if current < MIN_PYTHON:
        logger.error(
            "Python %d.%d required, but running %d.%d",
            *MIN_PYTHON,
            *current,
        )
        return False
    logger.info("Python %d.%d ✓", *current)
    return True


def _check_packages() -> bool:
    """Verifies all required third-party packages are importable."""
    all_ok = True
    for import_name, pip_name in REQUIRED_PACKAGES:
        try:
            importlib.import_module(import_name)
            logger.info("Package '%s' ✓", pip_name)
        except ImportError:
            logger.error("Package '%s' is missing (pip install %s)", pip_name, pip_name)  # noqa: TRY400
            all_ok = False
    return all_ok


def _check_job_scripts(jobs_dir: Path) -> bool:
    """Verifies expected job scripts exist in the jobs directory."""
    all_ok = True
    for name in EXPECTED_JOBS:
        path = jobs_dir / name
        if path.is_file():
            logger.info("Job script '%s' ✓", name)
        else:
            logger.error("Job script '%s' not found at %s", name, path)
            all_ok = False
    return all_ok


def _create_outputs_dir(base_dir: Path) -> bool:
    """Creates the outputs directory for cached reports."""
    outputs_dir = base_dir / "outputs"
    try:
        outputs_dir.mkdir(parents=True, exist_ok=True)
        logger.info("Output directory '%s' ✓", outputs_dir)
    except OSError:
        logger.exception("Failed to create output directory at %s", outputs_dir)
        return False
    return True


def main() -> None:
    """Runs all environment checks and prepares the workspace."""
    setup_standalone_logging()

    logger.info("Running environment setup...")

    jobs_dir = Path(__file__).resolve().parent
    base_dir = jobs_dir.parent

    checks = [
        _check_python_version(),
        _check_packages(),
        _check_job_scripts(jobs_dir),
        _create_outputs_dir(base_dir),
    ]

    if all(checks):
        logger.info("All checks passed — environment is ready.")
    else:
        logger.error("Some checks failed. Review the output above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
