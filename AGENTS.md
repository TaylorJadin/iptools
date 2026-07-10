# AGENTS.md

Guidance for agentic coding tools working in this repository.

## Overview

`iptools` is a single-file Python 3 command-line tool for extracting, expanding,
and summarizing IP addresses, CIDR ranges, and ASNs from arguments, files, or
stdin. All logic lives in `iptools.py`. There is no package layout and no build
step.

Subcommands:

- `info` — show ipinfo.io, BGP range, ASN, and hostname lookup details.
- `expand` — expand CIDRs, ASNs, and IPs into individual IP addresses.
- `condense` — identify common IPs, ASNs, and CIDR prefixes from a set of IPs.

See `README.md` for user-facing usage and configuration details.

## Conventions

- **Standard library only.** Do not add third-party runtime or test
  dependencies. The tool must run with a bare Python 3 interpreter. Network
  lookups use `urllib` and `socket`; everything else uses `ipaddress`, `re`,
  `argparse`, `json`, etc.
- **Python 3.6 compatibility.** Type hints are written as `# type:` comments
  (not inline annotations) so the code parses on older interpreters. Keep new
  code in this style and avoid f-strings — use `str.format`, matching the
  existing code.
- **Pure vs. network functions.** Small pure helpers (parsing, filtering,
  formatting, config reading, skip-rule logic) are kept separate from functions
  that hit the network. Prefer adding logic to a testable pure helper.
- Match the surrounding style: module-level functions, `NamedTuple` for simple
  records, and warnings/errors printed to `sys.stderr`.

## Running

```sh
./iptools.py info 8.8.8.8
./iptools.py expand 192.0.2.0/30
./iptools.py condense 1.1.1.1 8.8.8.8
```

## Testing

Tests use the standard-library `unittest` module (no pytest, no dependencies)
and cover the pure, non-network helpers. Run the full suite from the repo root:

```sh
python3 -m unittest discover -s tests -v
```

Or run a single module:

```sh
python3 -m unittest tests.test_iptools -v
```

When adding features, prefer factoring logic into pure helpers and adding
`unittest` cases in `tests/`. Do not write tests that make real network calls.
