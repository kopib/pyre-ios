# ☁️ rclone & iCloud Drive Setup Guide (Linux/Ubuntu)

This guide walks you through setting up **rclone** on Linux (such as Ubuntu) to wirelessly sync files directly into your iOS **a-Shell** app folder on iCloud Drive.

For more information, refer to the official [rclone GitHub page](https://github.com/rclone/rclone).

---

## 🛠️ Step 1: Install rclone on Linux

If you do not have rclone installed yet, run the official installation script:
```bash
sudo -v && curl https://rclone.org/install.sh | sudo bash
```
*(For alternative install methods, check the [Official rclone download page](https://rclone.org/downloads/))*

---

## ⚙️ Step 2: Configure the iCloud Drive Remote

Rclone v1.69+ includes native support for Apple iCloud.

1. Open your terminal and start configuration:
   ```bash
   rclone config
   ```
2. Press **`n`** to create a new remote.
3. Enter a custom name for your remote (e.g. `icloud` or `my_icloud`).

> [!IMPORTANT]
> The remote name (e.g. `icloud`) is user-defined. Whenever you see `icloud:a-Shell/jobs/` in the commands, replace `icloud` with whatever name you chose during this setup.

4. When prompted for the storage type, type **`iclouddrive`** (or select it from the list).
5. Enter your standard Apple ID username and password when prompted.
   * *Note: Do not use an App-Specific Password; use your standard Apple ID credentials.*
6. Complete the two-factor authentication (2FA) flow by entering the verification code sent to your trusted Apple devices.
7. When asked to choose the service type, choose **`drive`** (for iCloud Drive).
8. Save and exit the configuration.

---

## 🔄 Step 3: Wirelessly Syncing Files

Once configured, sync your local `jobs/` directory to iCloud using:
```bash
# Syntax: rclone copy jobs/ <YOUR_REMOTE_NAME>:a-Shell/jobs/
rclone copy jobs/ icloud:a-Shell/jobs/
```
*(Replace `icloud` with your chosen remote name)*

> [!NOTE]
> Apple's trust token is valid for 30 days. If the sync fails after a month, run `rclone config reconnect <YOUR_REMOTE_NAME>:` to re-authenticate with a new 2FA code.

---

## 📂 Step 4: Manual File Copy Alternative (No rclone)

If you prefer not to use `rclone`, you can copy your script files manually:

### Option A: Using the iCloud Web Interface
1. Open a web browser on your computer and go to [icloud.com](https://www.icloud.com/).
2. Log in with your Apple ID.
3. Open **iCloud Drive** and find the **a-Shell** folder.
4. Upload the `jobs/` folder (or individual files like `jobs/finanzen_net.py` and `jobs/utils/`) directly into the `a-Shell/` directory.

### Option B: Using a macOS Device
If you have access to a Mac:
1. Locate the **a-Shell** folder in the Finder under iCloud Drive.
2. Drag and drop the `jobs/` directory directly into the Finder folder.
3. iCloud will automatically sync the files to your iOS device.
