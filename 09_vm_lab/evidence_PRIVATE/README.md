# Lab evidence (private)

Raw output from the two lab boots. **Not published**: it holds process lists with window titles, system details, packet captures and the DNS log of the owner's real software.

| Path | What it is |
|---|---|
| `offline_boot/collector_output/` | Everything `collect.bat` wrote in the offline boot (process list, services, scheduled tasks, loader-folder listings, Defender status…) |
| `offline_boot/guest.pcap` | Full packet capture of the guest, offline boot |
| `online_boot/pre_close_snapshot/` | Process list and connections recorded **before** user apps were closed |
| `online_boot/collector_output/` | `collect.bat watch` output (10 of 18 rounds; the run was cut short) |
| `online_boot/guest.pcap` | The guest's own packet capture |
| `online_boot/bridge_capture.pcap` | Second capture taken on the host's bridge |
| `online_boot/dns.log` | The lab DNS forwarder's query log |
| `*.sha256` | Hashes taken when the files were copied out |

Handle as malware-adjacent data: read with text tools, never run anything from it. The curated public summary is [`../results/dns_names_online_run.txt`](../results/dns_names_online_run.txt).
