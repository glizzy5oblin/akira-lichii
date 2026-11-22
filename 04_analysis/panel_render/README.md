# panel_render: the "Akira Remote" control panel, rendered

The attacker's web control panel was carved byte-for-byte out of the RAT's memory (see [`../panel_source/`](../panel_source/)). This folder runs that carved code against a **mock backend with fake data**, so you can see what the operator saw without any malware or real victim data.

> **All data in these screenshots is fake.** Hostname `DESKTOP-DEMO01`, user `demo`, `example.test` domains, documentation-range IPs (`203.0.113.x`, `198.51.100.x`, `192.0.2.x`), `FAKE-…` identifiers. The mock server binds `127.0.0.1` and makes no outbound connections (only the Font Awesome icon CSS comes from cdnjs).

<p align="center">
  <img src="screenshots/00_main.png" alt="Main view: live screen stream of the victim desktop" width="900"><br>
  <sub><b>Main view.</b> The live remote-desktop stream with its toolbar: restart, quality, audio, fullscreen, screenshot, clipboard, keyboard. The desktop picture is a placeholder; the real panel streams the victim's screen as JPEG frames. The left rail holds the five tool menus below.</sub>
</p>

**Contents:** [Tool menus](#tool-menus) · [Tools](#tools) · [Limits of the mock](#limits-of-the-mock) · [Run it yourself](#run-it-yourself) · [Files](#files)

---

## Tool menus

The left rail has five menus. Together they cover the features listed in `../panel_source/app.js.txt` (91 API routes + 6 websockets).

| Remote tools | System | Recovery |
|:---:|:---:|:---:|
| <img src="screenshots/15_menu_remote.png" alt="Remote tools menu" width="300"> | <img src="screenshots/16_menu_system.png" alt="System menu" width="300"> | <img src="screenshots/17_menu_recovery.png" alt="Recovery menu" width="300"> |
| File manager, keylogger, HVNC, hidden browsers, task manager, terminal, webcam, screenshot | System info, startup manager, scheduled tasks, services, TCP manager, registry editor, listening ports, SOCKS5 proxy, local users & RDP | Passwords, Discord tokens, cards & autofill, Wi-Fi passwords, browser history, recent documents, **Full Grab** |

| Miscellaneous | Power & client |
|:---:|:---:|
| <img src="screenshots/18_menu_misc.png" alt="Miscellaneous menu" width="300"> | <img src="screenshots/19_menu_client.png" alt="Power and client menu" width="300"> |
| Run exe / fetch, run to memory, open URL, Defender control, firewall control | Sessions, lock, sleep, hibernate, shutdown timer, reboot, restart remote, shut down, **Uninstall** |

A shield icon on an entry marks a tool that needs administrator rights on the victim. This victim's account was a local administrator.

---

## Tools

### Spying and remote control

| | |
|---|---|
| <img src="screenshots/04_keylogger.png" alt="Keylogger" width="420"> | <img src="screenshots/03_files.png" alt="File explorer" width="420"> |
| **Keylogger.** Keystrokes with timestamp and the window they were typed into, plus a clipboard tab. Filterable by app. | **File explorer.** An Explorer-style browser of the victim's drives with upload, zip, download, rename and delete. |
| <img src="screenshots/12_hidden_browsers.png" alt="Hidden browsers" width="420"> | <img src="screenshots/02_taskmgr.png" alt="Task manager" width="420"> |
| **Hidden browsers.** Start a browser session the user can't see, scan for browser cookies, and keep them in a "cookie vault" (RAM-only in this incident; see FINDINGS). | **Task manager.** Processes, GPU and services with an *End task* button per row. The `calc.exe` and `charmap.exe` rows are demo entries that mimic this incident's hollowed processes. |

### Credential theft ("Recovery")

| | |
|---|---|
| <img src="screenshots/08_passwords.png" alt="Saved passwords" width="420"> | <img src="screenshots/09_discord_tokens.png" alt="Discord tokens" width="420"> |
| **Saved passwords.** Browser, URL, user and password (masked until *Show*), with copy and CSV export. | **Discord tokens.** Account, source (LevelDB), email, 2FA and Nitro status, token (masked). |
| <img src="screenshots/10_wifi.png" alt="Wi-Fi passwords" width="420"> | |
| **Wi-Fi passwords.** Saved SSIDs with authentication type and key. Empty in the mock. | |

### System reconnaissance and persistence

| | |
|---|---|
| <img src="screenshots/01_sysinfo.png" alt="System info" width="420"> | <img src="screenshots/05_startup.png" alt="Startup manager" width="420"> |
| **System info.** Host, user, account type, OS, CPU, RAM, GPU, local and public IP, geolocation, ISP, MAC and a hardware ID. | **Startup manager.** Lists HKCU/HKLM autostart entries and lets the operator edit, disable or **add** one. This is the panel-side view of the persistence the loader used. |
| <img src="screenshots/06_tcp.png" alt="TCP manager" width="420"> | <img src="screenshots/07_ports.png" alt="Listening ports" width="420"> |
| **TCP manager.** Live connections per process, with per-connection chart and kill buttons. | **Listening ports.** Open ports per process and protocol. |
| <img src="screenshots/11_registry.png" alt="Registry editor" width="420"> | |
| **Registry editor.** Browse and edit all five hives: new key, new value, delete key. | |

### Running code and disabling defences

| | |
|---|---|
| <img src="screenshots/13_run_exe.png" alt="Run exe / fetch and run" width="420"> | <img src="screenshots/14_defender.png" alt="Defender control" width="420"> |
| **Run exe / Fetch & Run.** Runs a file already on the victim, or downloads one from a URL and runs it, optionally hidden. | **Defender control.** Disable or enable Defender features, add path exclusions, or remove Defender. The values shown are mock data. **In this incident Defender stayed on and the malware changed no settings** (FINDINGS §10). |

---

## Limits of the mock

- **No websockets.** The live screen, webcam, microphone, keylogger feed and terminal need them, so those views show placeholders or static rows. `00_main.png` uses a stand-in desktop image.
- **Read-only demo data.** Buttons render but do nothing. Nothing is sent anywhere.
- **Some tools show empty states** (Wi-Fi, registry, hidden browsers, file explorer below the drive list) because the mock returns no records for them.
- The screenshots show the panel's *design and features*. They are not evidence of what the attacker did on the victim. For that, see `01_report/FINDINGS_2026-11-21.md`.

---

## Run it yourself

Needs Node.js and, for the screenshots, `google-chrome-stable` on your `PATH` (the command is hardcoded in `mock/shoot.mjs`). From this folder:

```sh
node mock/server.mjs &                 # serves the carved panel and fake /api/* on http://127.0.0.1:8765/
xdg-open http://127.0.0.1:8765/        # or open that URL in a browser
node mock/shoot.mjs                    # headless Chrome: regenerate every PNG in screenshots/
```

The panel source files are named `.txt` for safety. `mock/server.mjs` serves them from `../panel_source/` and maps them to the names the panel expects.

> Two stylesheet names are swapped in the carve: `panel_source/theme.css.txt` is really the panel's `viewer.css`, and `extra_01_1106c4e.txt` is the real `theme.css` (design tokens).

---

## Files

| Path | What it is |
|---|---|
| `mock/server.mjs` | Serves the carved panel from `../panel_source` and answers `/api/*` with fake data. No websockets |
| `mock/shoot.mjs` | Headless Chrome via CDP: opens each tool and writes a PNG per tool to `screenshots/` |
| `screenshots/` | The 20 images shown above: `00_main`, `01`–`14` one per tool, `15`–`19` the menus |
| `panel_view.html`, `theme.css`, `panel_screenshot.png` | The first, JS-less static copy. Older and mostly blank; the mock above is better |
