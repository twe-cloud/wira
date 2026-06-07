# Wira Windows install — smoke checklist

Run this on a real Windows 11 x64 machine (Windows 10 x64 as a secondary target)
after the `Build Windows Installer` workflow publishes `WiraSetup.exe`. The build
artifact existing is NOT proof it works — only a pass here lets us call Windows
"buyer-safe beta" instead of "untested".

The installer is currently **unsigned**, so SmartScreen will warn. That is expected
for the beta; note it but don't treat it as a failure.

## Pre-req
- A clean Windows account that has never run Wira (so `~/.wira` starts empty).
- The exact `WiraSetup.exe` from the release under test (record the version/tag).

## Checklist

1. **Download + SmartScreen**
   - [ ] Download `WiraSetup.exe` from the site route `/download/wira-windows`.
   - [ ] SmartScreen warning appears → "More info" → "Run anyway" installs it.
   - [ ] Installer completes without admin elevation (it installs per-user, `PrivilegesRequired=lowest`).

2. **First launch**
   - [ ] Launching from the Start Menu / desktop shortcut opens the Wira window (no console window, no traceback dialog).
   - [ ] The welcome / setup screen renders with readable fonts (watch for Tk font/scaling issues at 125%/150% display scaling).

3. **State location (must be outside the install dir)**
   - [ ] After first run, `C:\Users\<you>\.wira\` exists.
   - [ ] `~/.wira/.env` is written there (NOT under `C:\Program Files` / the install folder).

4. **Capability detection**
   - [ ] The brain-choice screen reflects the machine honestly. On a 16 GB+ box the local-AI option should read as available (this is the RAM-detection fix — pre-fix it always said "limited").

5. **Pick a brain (cloud lane)**
   - [ ] Choose the free / ChatGPT lane and complete it. The key/credential is saved to `~/.wira/.env`.

6. **WhatsApp QR pairing**
   - [ ] The QR screen renders an actual scannable code.
   - [ ] Pair from a phone: WhatsApp → Linked Devices → Link a Device → scan.
   - [ ] Send the owner a message; Wira replies.

7. **Restart persistence**
   - [ ] Quit Wira, relaunch. It does NOT ask to re-pair or re-enter the brain (session + `.env` persisted in `~/.wira`).
   - [ ] If "Start Wira when I log in" was selected at install, confirm the `Startup` shortcut launches it on next login.

8. **Uninstall**
   - [ ] Uninstall via Settings → Apps removes the program.
   - [ ] `~/.wira` (buyer-owned data) is left intact, as designed.

## Record the result
- Tag/version tested, Windows version + build, RAM, display scaling.
- Pass/fail per step, with a screenshot of the welcome screen and the QR screen.
- File the result next to the other QA notes in `docs/qa/`.

Only after a clean pass: update `STATUS.md` to mark Windows as buyer-safe beta and,
if/when signed, drop the SmartScreen caveat from the site copy (`windowsBetaNote`).
