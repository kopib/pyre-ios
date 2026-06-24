# Contributing & Adding New Jobs

Thank you for contributing to the **pyre-ios** blueprint! This guide explains how to add new background automation jobs to the system, how to ensure they pass linter/validation checks, and best practices for managing your code.

---

## 🛠️ How to Add a New Job

Follow these steps to integrate a new script into the background execution framework:

### 1. Create your script under `jobs/`
Create a new standalone Python file (e.g., `jobs/weather_alert.py`). 

Ensure your script:
* Imports and uses the standalone logger:
  ```python
  import logging
  from utils.logger import setup_standalone_logging
  
  logger = logging.getLogger(__name__)
  ```
* Implements a `main()` function:
  ```python
  def main() -> None:
      setup_standalone_logging()
      logger.info("Running weather alert...")
      # Your logic here
  ```
* Saves any outputs or cached files to the root-level `outputs/` folder (which resolves to `../outputs` relative to the script).

### 2. Update `jobs/setup.py`
To make sure your new job is tracked and validated by the setup wizard:
1. Open `jobs/setup.py`.
2. Locate the `EXPECTED_JOBS` list:
   ```python
   EXPECTED_JOBS: Final[list[str]] = [
       "finanzen_net.py",
       "weather_alert.py",  # Add your new job script here
   ]
   ```
3. If your script introduces new third-party dependencies, add them to `REQUIRED_PACKAGES` in the format `("import_name", "pip-package-name")`:
   ```python
   REQUIRED_PACKAGES: Final[list[tuple[str, str]]] = [
       ("bs4", "beautifulsoup4"),
       ("curl_cffi", "curl-cffi"),
       ("requests", "requests"),
       ("feedparser", "feedparser"),  # Example dependency
   ]
   ```

### 3. Update Project Dependencies
Run `uv` to add the new dependency to your local `pyproject.toml` and lockfile:
```bash
uv add feedparser
```

### 4. Run Linter & Validation
Before pushing, ensure the code satisfies formatting and lint rules:
```bash
uv run ruff check .
uv run python jobs/setup.py
```

---

## 🔒 How to Safeguard Your Repository (Avoid Overwrites)

To avoid accidentally losing or overwriting your scripts or local generated data, follow these best practices:

### 1. `rclone copy` vs `rclone sync`
* **Use `rclone copy` (Safe):** This only adds/updates files at the destination. It will **not** delete any files on your iOS device (such as locally generated `.txt` reports, logs, or photos).
* **Avoid `rclone sync` (Unsafe):** `rclone sync` makes the destination identical to the source. If you run it, it will **permanently delete** any files in your iCloud `a-Shell/` directory that do not exist on your computer.

### 2. Pulling generated data back to Linux
If your scripts generate reports or write log files on iOS, you can safely pull them back to your computer without overwriting your source code:
```bash
# Safely copy outputs from iOS back to your local outputs folder
rclone copy icloud:a-Shell/outputs/ outputs/
```

### 3. Git Safety Rules
* **Never force push (`git push --force`):** If GitHub rejects your push, always pull and rebase (`git pull origin main --rebase`) first. Force pushing can overwrite and delete history on GitHub that was committed from another machine.
* **Commit early and often:** Even if a feature is half-finished, a local commit acts as a backup state. If you make a mistake, you can always revert to it using `git reflog` or `git reset`.
* **Use branches for experiments:** If you are testing a complex new scraper, write it on a feature branch:
  ```bash
  git checkout -b feature/new-scraper
  ```
