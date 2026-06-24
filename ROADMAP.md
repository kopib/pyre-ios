# 🗺️ Headless iOS Server Blueprint - Roadmap

This roadmap outlines planned features, developer experience (DX) enhancements, and reliability improvements for the Headless iOS automation framework.

---

## 🛠️ Phase 1: Developer Experience & Automation

### 1. Interactive CLI Setup Script (`setup.py`)
Create a terminal setup wizard to automate the initial configuration of the local development machine and iCloud synchronization:
- [ ] **Dependency Audit:** Auto-detect and install required local packages via `uv` or `pip`.
- [ ] **rclone Health Check:** Verify the active `rclone` installation and validate connection status with the custom iCloud remote.
- [ ] **Interactive Remote Setup:** Prompt the user to select or name their iCloud remote and perform a test file transfer.
- [ ] **First-run Validation:** Remotely execute the script inside a-Shell and verify the automatic creation of the `outputs/` folder.

### 2. Multi-Job Scheduler & Runner
Enhance the runner architecture to support scheduling and running multiple independent background scripts:
- [ ] Implement a unified runner script (e.g. `jobs/run_all.py`) that acts as a single execution entry point for iOS.
- [ ] Introduce custom configuration profiles (e.g. JSON or YAML) to customize target scrapers and execution times.

---

## 📊 Phase 2: Resilience & Error Handling

### 1. Robust Local Logging & Error Auditing
Ensure issues (like network failures or structural HTML changes on target sites) are logged and reportable:
- [ ] Redirect script exception tracebacks to a dedicated `outputs/errors.log` file.
- [ ] Expose an error flag in the outputs directory that the iOS Shortcut can check, allowing it to send an alert message if a task fails.

### 2. Telemetry & Server Heartbeats
Monitor the health and uptime of the headless iOS device:
- [ ] Implement a simple daily telemetry script to check internet connectivity and battery levels, writing the stats to `outputs/system_health.json`.
- [ ] Connect the telemetry log with a status monitor dashboard or trigger an alert if a heartbeat is missed.

---

## 🔗 Phase 3: Ecosystem Extensions

### 1. Multi-Channel Notification Support
Add alternative messaging and delivery layers as fallbacks if iMessage is unavailable:
- [ ] Integrate optional Discord Webhooks, Telegram Bot APIs, or **ntfy.sh** wireless deliveries.
- [ ] Standardize payload formatting across all message brokers.

### 2. Custom Web Configuration UI
Create a lightweight Web UI (running locally or inside the home network) to view log histories, scrape caches, and configure schedules.
