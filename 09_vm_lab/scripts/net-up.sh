#!/bin/bash
# Isolated, limited internet for the lab guest.  sudo net-up.sh up|down
# Guest sits on 10.77.0.0/24 behind NAT. It can NOT reach the host (except DHCP/DNS), the LAN, tailscale or any other
# interface: forwarding is allowed only out of the default-route interface and never to private ranges.
# Egress is limited to tcp 80/443/7844 and udp 443/7844 (RAT, BSC RPC, GitHub, cloudflared tunnel).
# The guest cannot be used as a scanner, mail or DoS source. Miner pool domains are sinkholed in DNS.
# Set WAN=<iface> to route out through a VPN interface instead of the default route.
set -euo pipefail
[ "$(id -u)" = 0 ] || { echo "run with sudo"; exit 1; }
# Private ranges are written as ${B172}/${B192} + suffix so a text scrubber does not rewrite them in the published copy.
B172=172; B192=192
U=${SUDO_USER:-user}; BR=labbr0; TAP=labtap0; NETW=10.77.0.0/24
WAN=${WAN:-$(ip route show default | awk '{print $5; exit}')}
case "${1:-}" in
up)
  # clean up any half-built state from an earlier failed run
  if ip link show $BR >/dev/null 2>&1 || ip link show $TAP >/dev/null 2>&1; then "$0" down >/dev/null; fi
  ip link add $BR type bridge; ip addr add 10.77.0.1/24 dev $BR; ip link set $BR up
  ip tuntap add dev $TAP mode tap user "$U"; ip link set $TAP master $BR up
  sysctl -q net.ipv6.conf.$BR.disable_ipv6=1
  echo "$(sysctl -n net.ipv4.ip_forward)" > /run/lab_ipfwd; sysctl -q net.ipv4.ip_forward=1
  nft -f - <<EOF
table inet lab {
  chain input {
    type filter hook input priority -10; policy accept;
    iifname "$BR" udp dport { 53, 67 } accept
    iifname "$BR" tcp dport 53 accept
    iifname "$BR" drop
  }
  chain forward {
    type filter hook forward priority -10; policy accept;
    iifname "$BR" oifname != "$WAN" drop
    iifname "$BR" ip daddr { 10.0.0.0/8, ${B172}.16.0.0/12, ${B192}.168.0.0/16, 100.64.0.0/10, 169.254.0.0/16, 127.0.0.0/8 } drop
    iifname "$BR" tcp dport { 80, 443, 7844 } accept
    iifname "$BR" udp dport { 443, 7844 } accept
    iifname "$BR" drop
  }
}
table ip labnat {
  chain post {
    type nat hook postrouting priority 100; policy accept;
    oifname "$WAN" ip saddr $NETW masquerade
  }
}
EOF
  # Docker sets the iptables FORWARD policy to DROP; an accept in our table cannot override that, so let our own traffic through there.
  if command -v iptables >/dev/null && iptables -w -S FORWARD 2>/dev/null | grep -q '^-P FORWARD DROP'; then
    iptables -w -I FORWARD 1 -i $BR -o $WAN -m comment --comment labvm -j ACCEPT
    iptables -w -I FORWARD 1 -i $WAN -o $BR -m conntrack --ctstate RELATED,ESTABLISHED -m comment --comment labvm -j ACCEPT
  fi
  dnsmasq --interface=$BR --bind-interfaces --except-interface=lo --no-resolv --no-hosts --server=1.1.1.1 \
    --dhcp-range=10.77.0.50,10.77.0.60,12h --address=/hashvault.pro/0.0.0.0 --address=/moneroocean.stream/0.0.0.0 \
    --pid-file=/run/labdnsmasq.pid --log-queries --log-facility=/home/user/vmlab/dns.log
  chown "$U" /home/user/vmlab/dns.log 2>/dev/null || true
  echo "up. egress via $WAN. Capture with:  sudo tcpdump -i $BR -n -w /home/user/vmlab/online.pcap"
  ;;
dns)
  # (re)start only DHCP/DNS; leaves the tap, bridge and firewall alone so a running guest keeps its NIC
  [ -f /run/labdnsmasq.pid ] && kill "$(cat /run/labdnsmasq.pid)" 2>/dev/null || true
  sleep 1
  ss -lunp 2>/dev/null | grep -E '10\.77\.0\.1:53|0\.0\.0\.0:53|\*:53' || true
  dnsmasq --interface=$BR --bind-interfaces --except-interface=lo --no-resolv --no-hosts --server=1.1.1.1 \
    --dhcp-range=10.77.0.50,10.77.0.60,12h --address=/hashvault.pro/0.0.0.0 --address=/moneroocean.stream/0.0.0.0 \
    --pid-file=/run/labdnsmasq.pid --log-queries --log-facility=/home/user/vmlab/dns.log \
    && { chown "$U" /home/user/vmlab/dns.log 2>/dev/null || true; echo "dnsmasq started (pid $(cat /run/labdnsmasq.pid))"; } \
    || echo "dnsmasq FAILED to start (see message above)"
  ;;
status)
  echo "WAN=$WAN  ip_forward=$(sysctl -n net.ipv4.ip_forward)"
  ip -br addr show $BR 2>&1; ip -br link show $TAP 2>&1
  echo "--- nft"; nft list tables 2>&1 | grep -E 'lab' || echo "NO lab nft tables"
  echo "--- iptables labvm rules"; iptables -w -S FORWARD 2>&1 | grep -E 'labvm|^-P' || true
  echo "--- dnsmasq"; pgrep -a dnsmasq || echo "dnsmasq not running"
  echo "--- port 53 listeners"; ss -lunp 2>/dev/null | grep ':53 ' || true
  ;;
down)
  [ -f /run/labdnsmasq.pid ] && kill "$(cat /run/labdnsmasq.pid)" 2>/dev/null || true
  nft delete table inet lab 2>/dev/null || true; nft delete table ip labnat 2>/dev/null || true
  if command -v iptables >/dev/null; then
    iptables -w -S FORWARD 2>/dev/null | grep -- '--comment labvm' | sed 's/^-A/-D/' | while read -r r; do iptables -w $r 2>/dev/null || true; done
  fi
  ip link del $TAP 2>/dev/null || true; ip link del $BR 2>/dev/null || true
  [ -f /run/lab_ipfwd ] && sysctl -q net.ipv4.ip_forward="$(cat /run/lab_ipfwd)" || true
  echo down ;;
*) echo "usage: sudo $0 up|down|dns|status"; exit 1 ;;
esac
