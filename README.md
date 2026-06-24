
<p align="center">
  <img src="assets/images/logo.png" alt="Headless iOS Python Server Logo" width="180" height="180">
</p>

# 📱 Headless iOS Python Server & Automation Blueprint


Transform your retired iOS devices into silent, low-power, zero-cost background utility servers.

---

## 📂 Project Architecture

```text
.
├── README.md               # Project overview, quickstart, & entry point
├── ROADMAP.md              # Future features & project expansion plans
├── pyproject.toml          # Project configuration & package dependencies
├── uv.lock                 # Strict dependency lockfile
├── .python-version         # Pinned Python runtime version
├── assets/
│   └── images/             # Logo & documentation screenshots
├── docs/
│   ├── ios_setup.md        # iOS environment setup guide
│   ├── ios_automation.md   # iOS Shortcuts integration guide
│   ├── rclone_setup.md     # rclone & iCloud sync guide
│   └── hardware.md         # Battery longevity & smart plug guide
└── jobs/
    ├── __init__.py
    ├── setup.py            # Environment validation & folder setup
    ├── utils/
    │   ├── __init__.py
    │   └── logger.py       # Standalone stderr logging configuration
    └── finanzen_net.py     # Standalone scraper & aggregator script
```

---

## 🔧 Installation & Local Setup

### 1. Clone & Set Up Virtual Environment
Ensure you have `uv` installed. Set up dependencies and run the linter:
```bash
uv sync
uv run ruff check .
```

### 2. Execute Locally
To execute the scraping job and cache the plain-text SMS payload locally:
```bash
uv run jobs/finanzen_net.py
```

---

## ☁️ iOS Deployment Workflow


### Step 1: Deploying the Script to iOS
To run the script on iOS, your device must be configured with the **a-Shell** app and have iCloud Drive enabled. If you haven't set this up yet, please follow the [📱 iOS Environment Setup Guide](docs/ios_setup.md) first.

Once your environment is set up, transfer the `jobs/` folder into your `a-Shell/` iCloud Drive directory using one of these methods:

* **Method A: Automated Sync via `rclone` (Recommended)**

  Automatically sync files wirelessly. For instructions on installing rclone on Linux (Ubuntu), configuring the Apple iCloud Drive backend, and setting up your remote name, see the [☁️ rclone & iCloud Drive Setup Guide](docs/rclone_setup.md).
  ```bash
  # Syntax: rclone copy jobs/ <YOUR_REMOTE_NAME>:a-Shell/jobs/
  rclone copy jobs/ icloud:a-Shell/jobs/
  ```

* **Method B: Manual File Copy**

  Manually copy the files if you do not want to use rclone. For instructions using the iCloud Web Portal or macOS Finder, see the [Manual Transfer Guide](docs/rclone_setup.md#manual-file-copy-alternative-no-rclone).

### Step 2: Validate the Environment
After syncing, run the setup script inside **a-Shell** on your iOS device to verify everything is in place:
```bash
cd ~cloud/jobs
python setup.py
```
This checks the Python version, verifies required packages are installed, confirms job scripts are present, and creates the `outputs/` directory.

> [!NOTE]
> In a-Shell, `~cloud` is a built-in alias that points to the app's iCloud Drive container. All files synced via rclone are accessible through this path.

### Step 3: Run a Job
Once setup passes, execute a job script to generate and cache the report:
```bash
python finanzen_net.py
```
This generates the plain text report and caches it locally as `a-Shell/outputs/finanzen_net_sms.txt`.

---

## 📖 Documentation & Guides

For complete configuration and hardware safety details, explore the project guides:

* [📱 iOS Environment Setup](docs/ios_setup.md) — How to install a-Shell and configure the iCloud directory structure.
* [☁️ rclone & iCloud Sync](docs/rclone_setup.md) — How to configure rclone on Linux/Ubuntu or copy files manually.
* [🐚 iOS Shortcuts Automation](docs/ios_automation.md) — Step-by-step instructions to build the silent 4-block message automation.
* [🔌 Battery Longevity & Smart Plug](docs/hardware.md) — How to protect your legacy phone's battery using automated smart plugs.
* [🗺️ Project Roadmap](ROADMAP.md) — Future features, automation scripts, and project expansion plans.