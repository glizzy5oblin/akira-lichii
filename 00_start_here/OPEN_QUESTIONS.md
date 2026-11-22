# Open questions

What is still unknown, grouped by area, with what would answer each one. Updated 2026-11-21 after the VM lab.

## Attacker activity

| Question | Why it is open | What would answer it |
|---|---|---|
| What did the operator do during the 14 days? | Dumps cover only the last session, the file-change journal only the last 7.5 hours, SRUM kept no network data | Probably cannot be answered from this machine. Assume the worst for anything stored or typed on it |
| Is the operator still trying to connect? | Lab boots were ≈9 minutes online; autostart was already removed | A longer online boot with the loader restored (emulator run), or a watch on the C2 names |

## The infected desktop

| Question | What would answer it |
|---|---|
| Anything left staged on disk? | Run [`DESKTOP_PREWIPE_CHECK.ps1.txt`](../01_report/DESKTOP_PREWIPE_CHECK.ps1.txt). The offline file table shows no Fonts executable or leftover `akdb*` folder |
| What did the short-lived `cmd.exe`, `chrome.exe` and `dllhost.exe` do at each login; where does `python.zip` come from? | Dynamic analysis in the lab with per-process logging |
| What served `localhost:49912`? | The panel code suggests the RAT itself; not proven |
| Is the `lichii.exe` still on the disk the trojanized build? | Hash it on a read-only mount and compare it with the analyzed sample ([lab open items](../09_vm_lab/RESULTS.md#open-items)) |

## The malware's internals

| Question | What would answer it |
|---|---|
| `t_id.txt` encoding | More decompilation; not yet decoded |
| What does the blockchain contract return *today*? | A live `eth_call`. Needs permission to query outward |
| Did the miner and Defender-tamper code ever run on the desktop? | Nothing seen in logs; the lab did not run them |
| The `DisplayUpdater` helper's 16-byte suffix, Telegram strings, wallet value | Further passes ([`stage2_boing_e87b/README.md`](../04_analysis/stage2_boing_e87b/README.md)) |

## Other devices

| Question | What would answer it |
|---|---|
| Was the Linux NVMe *read* from Windows? | Reads leave no trace; writes were ruled out |
| Does the router forward SSH from the internet to the server? | Check the router; the stolen key was used through the router on 11/13 |

## From the VM lab (new)

| Question | What would answer it |
|---|---|
| Two unexplained names: `dmu0adc7oht39.cloudfront.net` and `u05srooyhc.execute-api.us-east-1.amazonaws.com` | Process attribution in a longer run, or a public lookup (needs permission) |
| 51 connections with no DNS lookup (likely VPN relays) | Capture with visible names, or the VPN's relay list |
| Where did the newer, validly signed `bootmgfw.efi` on the EFI partition come from? | The owner (Windows media or a Secure Boot certificate update); a Microsoft hash lookup |
| Is the AI-agent app (installed after the infection) the owner's, and what is the autostart task "Start VMware VM"? | The owner |
| Cause of the 60 GB overlay growth | Probably Windows maintenance (hypothesis); not proven |
| Did the VM hide well enough for the sample to run? | A better-disguised VM; see [`SETUP.md`](../09_vm_lab/SETUP.md#what-the-vm-cannot-hide) |

## Owner decisions

- Have credentials been rotated (server password, SSH key, browser-saved logins, the AI-agent app's `.env`, tokens)? The checklist assumes **no** until confirmed.
