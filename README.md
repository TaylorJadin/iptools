# Taylor's IP Tools

Small command-line utilities for extracting, expanding, and summarizing IP
addresses, CIDR ranges, and ASNs from arguments, files, or stdin.

- `iptools info` shows IP, BGP range, ASN, and hostname lookup details.
- `iptools expand` expands CIDRs, ASNs, and IPs into individual IP addresses.
- `iptools condense` identifies common IPs, ASNs, and CIDR prefixes from a set of IPs.

All tools are Python 3 scripts and use only the Python standard library. Network
lookups use public services including ipinfo.io, RIPEstat, asn.ipinfo.app, and
Team Cymru WHOIS.

## Running these scripts 

Run the tool directly from the repo:

```sh
./iptools info 8.8.8.8
./iptools expand 192.0.2.0/30
./iptools condense 1.1.1.1 8.8.8.8
```

Or symlink it into `/usr/local/bin`:

```sh
ln -sf "/path/to/repo/iptools" /usr/local/bin/iptools
```

## Usage

Show details for an IP, ASN, or hostname:

```sh
iptools info 8.8.8.8
iptools info AS15169
iptools info example.com
```

Extract IPs and ASNs from arbitrary input:

```sh
curl -s https://api.github.com/meta | iptools info --short -4
```

Expand CIDRs or ASNs:

```sh
iptools expand 192.0.2.0/30
iptools expand -4 AS15169
curl -s https://api.github.com/meta | iptools expand -4
```

Summarize common IPs, ASNs, and prefixes from a list of IPs:

```sh
iptools condense 1.1.1.1 8.8.8.8
iptools condense --ip --min-count 2 access.log
iptools condense ips.txt
curl -s https://api.github.com/meta | iptools condense --cidr --short
```

Use `iptools --help` to list commands, or `iptools <command> --help` for the
full option list for a command.
