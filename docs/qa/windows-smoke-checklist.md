# Wira Windows install — smoke checklist

Run this on a real Windows 11 x64 machine (Windows 10 x64 as a secondary target)
after the `Build Windows Installer` workflow publishes a signed `WiraSetup.exe`.
The build artifact existing is NOT proof it works. The initial hardware pass was
recorded before the Windows route went live on 2026-07-10; rerun this checklist
after material installer, GUI, pairing, or persistence changes and before broad
paid traffic.

## Pre-req
- A clean Windows account that has never run Wira (so `~/.wira` starts empty).
- The exact signed `WiraSetup.exe` **from the `Build Windows Installer` workflow
  run under test** — record its run ID and commit SHA.

  For a candidate build, use the exact workflow artifact first. After publishing,
  repeat signature verification against the release asset because that is the
  binary the Worker serves.

## Checklist

1. **Download + trust**
   - [ ] Download the exact signed `WiraSetup.exe` from the workflow run under test.
   - [ ] Confirm Windows identifies the installer as signed by Ni Biashara LLC.
   - [ ] SmartScreen does not present the unsigned-unknown-publisher path.
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

For every new Windows release, proceed in this order after a clean pass:

1. Cut a tagged release so the **signed** `WiraSetup.exe` becomes a release asset.
2. Verify the published asset is the signed one — `scripts/verify-authenticode.py`
   against the file downloaded from `releases/latest`, not the workflow artifact.
   The Worker serves the release, so an unverified release asset is what buyers get.
3. Update `STATUS.md`.
4. Confirm the Worker Windows route resolves to that exact verified asset.

Skipping step 2 is how an unsigned installer reaches a buyer despite a green
smoke test: the smoke test validates the artifact, the Worker serves the release.
