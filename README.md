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
./iptools.py info 8.8.8.8
./iptools.py expand 192.0.2.0/30
./iptools.py condense 1.1.1.1 8.8.8.8
```

Or symlink it into `/usr/local/bin`:

```sh
ln -sf "/path/to/repo/iptools.py" /usr/local/bin/iptools
```

## Config

Create a config file from the example:
```
cp iptools.conf.example iptools.conf 
```

`iptools` loads config from `iptools.conf` next to the real script location,
`~/.config/iptools/config`, `$IPTOOLS_CONFIG`, and any file passed with
`--config PATH`. If `iptools` is symlinked into a directory such as
`/usr/local/bin`, the executable-local config is still read from the symlink
target directory. Later files override boolean options. Skip entries are
cumulative.


```conf
skip_public_ip = false

[skip]
203.0.113.10
198.51.100.0/24
2001:db8::/32
AS64500
```

`skip_public_ip` skips the device's public IP address.

For one-off runs, pass `--skip VALUE` with an IP address, CIDR range, or ASN.
Repeat it to skip multiple values. Pass `--no-skip` to ignore all configured
and command-line skips for that run.

```sh
iptools --skip 203.0.113.10 expand 203.0.113.0/30
iptools condense --skip 198.51.100.0/24 access.log
iptools --no-skip info 203.0.113.10
```

Skip rules also apply to lookup-derived output where possible. For example, an
IP returned by `iptools info` is skipped when its lookup data belongs to a
skipped ASN, and `iptools condense` omits IP, CIDR, and ASN output discovered
from skipped Team Cymru lookup results.
Each command prints a summary line after its output, reporting how many items
were processed and, when skip rules apply, how many were skipped (for example,
`3 processed, 1 skipped`). The processed count reflects everything the command
handled, independent of any display limit such as `condense --top`. Pass
`--short` to omit the summary (and other headers), which is useful when piping
one command into another.
Non-short `condense` IP output includes ASN and ASN name details when lookup
data is available.

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
