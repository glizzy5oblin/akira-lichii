# What happened, in plain English

No jargon here; unfamiliar words are explained in the [glossary](GLOSSARY.md). Dates are 2026, local time.

## The short version

Someone searched for a game-console emulator called "Lichii" and landed on a **fake website** that looked official. The download from it was a real emulator with **malware added**. Running it handed a stranger remote control of the Windows desktop for about **two weeks** (Nov 7 → Nov 21). On Nov 21 it was found and shut down. Nothing suggests the other computers were infected, but a few passwords and one login key were exposed and should be changed.

## How it unfolded

```
 Nov 7            Nov 7–21                         Nov 21
   │                 │                                │
   ▼                 ▼                                ▼
 Fake site ──▶ Malware starts at every ──▶ Found, switched off,
 download      login and gives a stranger   evidence saved, checks
               remote access                 of other devices, lab test
```

1. **The trap.** A web search led to `lichii.org`, a lookalike of the real project. Its zip contained the emulator plus two extra files and a changed `lichii.exe`.
2. **Settling in.** On first run the malware created a fake "Python" folder and an autostart entry named *Microsoft Display Driver Manager*, a name chosen to look boring.
3. **Hiding.** At every login it started two normal Windows programs (Calculator and Character Map) and **swapped their insides** for its own code. In the task list they look harmless.
   - The "Character Map" copy was the **remote-access program** (called "Akira Remote"): it could watch the screen, webcam and microphone, log keystrokes, take files and read saved browser data.
   - The "Calculator" copy was a **tunnel** that put the attacker's control panel on the internet. The panel had **no password**, so in principle anyone who found its web address could have used it.
4. **Phoning home.** It found its operators through six website names and a **public blockchain record** used as a mailbox, which is hard to take down.
5. **Stealing.** At each login it copied the browsers' saved passwords, cookies and history for a moment, then deleted the copies.
6. **Not noticed.** Windows Defender raised no alarm.
7. **Discovery and containment (Nov 21).** The autostart was deleted and both disguised programs were frozen and saved for study.

## What we did afterwards

| Step | Where |
|---|---|
| Saved the evidence from the infected PC | `02_host_evidence/`, `03_memory_dumps/` |
| Took the malware apart *without running it* | `04_analysis/`, [`FINDINGS`](../01_report/FINDINGS_2026-11-21.md) |
| Checked the server, laptop, USB stick and Linux drive | `06_other_devices/` |
| Copied the infected Windows disk's logs for review | `08_windows_offline/` |
| Booted a **copy** of the infected Windows in a sandbox, offline and online, to see if anything was still active | [`09_vm_lab/`](../09_vm_lab/README.md) |

## Where things stand

- **Contained:** the malware no longer starts and was not seen contacting anything in the lab.
- **Not undone:** two weeks of exposure. Anything saved in the browsers or typed on that PC should be treated as stolen. The to-do list is [`ACTION_CHECKLIST.md`](../01_report/ACTION_CHECKLIST.md).
- **Not proven:** that the lab's quiet result means the machine is clean. The autostart was already gone, and a short quiet run is weak evidence. See [`OPEN_QUESTIONS.md`](OPEN_QUESTIONS.md).
- **Safe to say:** what the malware *could* do is well documented from its code; what the operator *actually did* during the 14 days is mostly unknown.

## Reading order

1. This page → 2. [`ACTION_CHECKLIST.md`](../01_report/ACTION_CHECKLIST.md) → 3. [`09_vm_lab/README.md`](../09_vm_lab/README.md) → 4. [`FINDINGS`](../01_report/FINDINGS_2026-11-21.md) when you want the technical detail.
