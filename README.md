# Taylor's IP Tools

Small command-line utilities for extracting, expanding, and summarizing IP
addresses, CIDR ranges, and ASNs from arguments, files, or stdin.

- `ipinfo` shows IP, BGP range, ASN, and hostname lookup details.
- `ipexpand` expands CIDRs, ASNs, and IPs into individual IP addresses.
- `ipcondense` identifies common ASNs and CIDR prefixes from a set of IPs.

All tools are Python 3 scripts and use only the Python standard library. Network
lookups use public services including ipinfo.io, RIPEstat, asn.ipinfo.app, and
Team Cymru WHOIS.

## Running these scripts 

Run the tools directly from the repo:

```sh
./ipinfo 8.8.8.8
./ipexpand 192.0.2.0/30
./ipcondense 1.1.1.1 8.8.8.8
```

Or symlink them into `/usr/local/bin`:

```sh
ln -sf "/path/to/repo/ipinfo" /usr/local/bin/ipinfo
ln -sf "/path/to/repo/ipexpand" /usr/local/bin/ipexpand
ln -sf "/path/to/repo/ipcondense" /usr/local/bin/ipcondense
```

## Usage

Show details for an IP, ASN, or hostname:

```sh
ipinfo 8.8.8.8
ipinfo AS15169
ipinfo example.com
```

Extract IPs and ASNs from arbitrary input:

```sh
curl -s https://api.github.com/meta | ipinfo --short -4
```

Expand CIDRs or ASNs:

```sh
ipexpand 192.0.2.0/30
ipexpand -4 AS15169
curl -s https://api.github.com/meta | ipexpand -4
```

Summarize common ASNs and prefixes from a list of IPs:

```sh
ipcondense 1.1.1.1 8.8.8.8
ipcondense ips.txt
curl -s https://api.github.com/meta | ipcondense --cidr --short
```

Use `--help` on any tool for the full option list.
