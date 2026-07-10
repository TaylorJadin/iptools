"""Unit tests for the pure, non-network helpers in iptools.py.

Run with:  python3 -m unittest discover -s tests -v

These tests deliberately avoid any function that performs network I/O
(lookups, resolution, public-IP fetch). They exercise parsing, filtering,
formatting, config handling, and skip-rule logic.
"""

import os
import sys
import tempfile
import unittest

# Make the repo root importable so `import iptools` works regardless of cwd.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import iptools


class IsValidIpTests(unittest.TestCase):
    def test_valid_ipv4(self):
        self.assertTrue(iptools.is_valid_ip("8.8.8.8"))

    def test_valid_ipv6(self):
        self.assertTrue(iptools.is_valid_ip("2001:db8::1"))

    def test_invalid(self):
        self.assertFalse(iptools.is_valid_ip("999.1.1.1"))
        self.assertFalse(iptools.is_valid_ip("not-an-ip"))
        self.assertFalse(iptools.is_valid_ip(""))


class ExtractIpsTests(unittest.TestCase):
    def test_extracts_and_validates(self):
        text = "start 8.8.8.8 mid 2001:db8::1 end 999.1.1.1 nope"
        self.assertEqual(
            iptools.extract_ips(text),
            ["8.8.8.8", "2001:db8::1"],
        )

    def test_no_ips(self):
        self.assertEqual(iptools.extract_ips("nothing here"), [])


class ExtractAsnsTests(unittest.TestCase):
    def test_normalizes_case_and_value(self):
        self.assertEqual(
            iptools.extract_asns("as15169 and AS007 and AS64500"),
            ["AS15169", "AS7", "AS64500"],
        )

    def test_no_asns(self):
        self.assertEqual(iptools.extract_asns("no asn here"), [])


class FilterIpsTests(unittest.TestCase):
    def setUp(self):
        self.ips = ["8.8.8.8", "2001:db8::1", "1.1.1.1"]

    def test_ipv4_only(self):
        self.assertEqual(
            iptools.filter_ips(self.ips, include_ipv4=True, include_ipv6=False),
            ["8.8.8.8", "1.1.1.1"],
        )

    def test_ipv6_only(self):
        self.assertEqual(
            iptools.filter_ips(self.ips, include_ipv4=False, include_ipv6=True),
            ["2001:db8::1"],
        )

    def test_both(self):
        self.assertEqual(
            iptools.filter_ips(self.ips, include_ipv4=True, include_ipv6=True),
            self.ips,
        )


class UniqueItemsTests(unittest.TestCase):
    def test_preserves_order_and_dedupes(self):
        self.assertEqual(
            iptools.unique_items(["a", "b", "a", "c", "b"]),
            ["a", "b", "c"],
        )

    def test_empty(self):
        self.assertEqual(iptools.unique_items([]), [])


class IncludeFamiliesTests(unittest.TestCase):
    def test_neither_flag_defaults_to_both(self):
        self.assertEqual(iptools.include_families(False, False), (True, True))

    def test_ipv4_only(self):
        self.assertEqual(iptools.include_families(True, False), (True, False))

    def test_ipv6_only(self):
        self.assertEqual(iptools.include_families(False, True), (False, True))

    def test_both_flags(self):
        self.assertEqual(iptools.include_families(True, True), (True, True))


class ParseBoolTests(unittest.TestCase):
    def test_truthy(self):
        for value in ("1", "true", "YES", " on "):
            self.assertIs(iptools.parse_bool(value), True, value)

    def test_falsy(self):
        for value in ("0", "false", "NO", " off "):
            self.assertIs(iptools.parse_bool(value), False, value)

    def test_invalid(self):
        self.assertIsNone(iptools.parse_bool("maybe"))


class StripInlineCommentTests(unittest.TestCase):
    def test_hash_comment(self):
        self.assertEqual(iptools.strip_inline_comment("key = value  # note"), "key = value")

    def test_semicolon_comment(self):
        self.assertEqual(iptools.strip_inline_comment("key = value ; note"), "key = value")

    def test_comment_char_inside_quotes_is_kept(self):
        self.assertEqual(
            iptools.strip_inline_comment('key = "a # b"'),
            'key = "a # b"',
        )

    def test_escaped_comment_char_is_kept(self):
        self.assertEqual(
            iptools.strip_inline_comment(r"key = a\#b"),
            r"key = a\#b",
        )

    def test_no_comment(self):
        self.assertEqual(iptools.strip_inline_comment("plain value"), "plain value")


class CleanTargetTests(unittest.TestCase):
    def test_strips_whitespace(self):
        self.assertEqual(iptools.clean_target("  8.8.8.8  "), "8.8.8.8")

    def test_strips_trailing_comma(self):
        self.assertEqual(iptools.clean_target("8.8.8.8,"), "8.8.8.8")

    def test_strips_surrounding_quotes(self):
        self.assertEqual(iptools.clean_target('"8.8.8.8"'), "8.8.8.8")
        self.assertEqual(iptools.clean_target("'8.8.8.8'"), "8.8.8.8")

    def test_empty(self):
        self.assertEqual(iptools.clean_target("   "), "")


class NormalizeAsnTests(unittest.TestCase):
    def test_with_prefix(self):
        self.assertEqual(iptools.normalize_asn("AS15169"), "AS15169")

    def test_lowercase_prefix(self):
        self.assertEqual(iptools.normalize_asn("as15169"), "AS15169")

    def test_bare_number(self):
        self.assertEqual(iptools.normalize_asn("15169"), "AS15169")

    def test_strips_leading_zeros(self):
        self.assertEqual(iptools.normalize_asn("AS007"), "AS7")

    def test_not_asn(self):
        self.assertIsNone(iptools.normalize_asn("ASxyz"))
        self.assertIsNone(iptools.normalize_asn("8.8.8.8"))


class AsnNumberTests(unittest.TestCase):
    def test_valid(self):
        self.assertEqual(iptools.asn_number("AS15169"), "15169")
        self.assertEqual(iptools.asn_number(15169), "15169")

    def test_invalid(self):
        self.assertIsNone(iptools.asn_number("nope"))


class AsnFieldFromValuesTests(unittest.TestCase):
    def test_list(self):
        self.assertEqual(iptools.asn_field_from_values([701, "1239"]), "701 1239")

    def test_single_value(self):
        self.assertEqual(iptools.asn_field_from_values(15169), "15169")

    def test_skips_invalid(self):
        self.assertEqual(iptools.asn_field_from_values(["701", "bad"]), "701")


class FormatAsnFieldTests(unittest.TestCase):
    def test_single(self):
        self.assertEqual(iptools.format_asn_field("15169"), "AS15169")

    def test_multiple(self):
        self.assertEqual(iptools.format_asn_field("701 1239"), "AS701 AS1239")

    def test_empty(self):
        self.assertEqual(iptools.format_asn_field(""), "AS")


class FormatValueTests(unittest.TestCase):
    def test_scalar(self):
        self.assertEqual(iptools.format_value(42), "42")

    def test_dict_is_json_sorted(self):
        self.assertEqual(iptools.format_value({"b": 1, "a": 2}), '{"a": 2, "b": 1}')

    def test_list_is_json(self):
        self.assertEqual(iptools.format_value([1, 2]), "[1, 2]")


class FormatNumberTests(unittest.TestCase):
    def test_thousands_separator(self):
        self.assertEqual(iptools.format_number(1234567), "1,234,567")

    def test_numeric_string(self):
        self.assertEqual(iptools.format_number("1000"), "1,000")

    def test_non_numeric_falls_back(self):
        self.assertEqual(iptools.format_number("abc"), "abc")


class WhoisFirstTests(unittest.TestCase):
    def setUp(self):
        self.records = [
            [{"key": "as-name", "value": "EXAMPLE"}, {"key": "descr", "value": "Example Net"}],
        ]

    def test_case_insensitive_match(self):
        self.assertEqual(iptools.whois_first(self.records, "AS-NAME"), "EXAMPLE")

    def test_missing_key(self):
        self.assertEqual(iptools.whois_first(self.records, "country"), "")


class ClassifyPrefixTests(unittest.TestCase):
    def test_valid(self):
        net = iptools.classify_prefix("192.0.2.0/24")
        self.assertIsNotNone(net)
        self.assertEqual(str(net), "192.0.2.0/24")

    def test_invalid(self):
        self.assertIsNone(iptools.classify_prefix("not-a-prefix"))


class ExtractTargetsTests(unittest.TestCase):
    def test_mixed_targets(self):
        text = "AS15169 192.0.2.0/24 8.8.8.8 2001:db8::/32 garbage 999.1.1.1"
        self.assertEqual(
            iptools.extract_targets(text),
            ["AS15169", "192.0.2.0/24", "8.8.8.8", "2001:db8::/32"],
        )

    def test_rejects_invalid_cidr(self):
        # 300.0.0.0/8 matches the regex shape but is not a valid network.
        self.assertEqual(iptools.extract_targets("300.0.0.0/8"), [])


class SelectedSectionsTests(unittest.TestCase):
    class _Args(object):
        def __init__(self, ip=False, asn=False, cidr=False):
            self.ip = ip
            self.asn = asn
            self.cidr = cidr

    def test_none_selected_shows_all(self):
        self.assertEqual(iptools.selected_sections(self._Args()), (True, True, True))

    def test_only_ip(self):
        self.assertEqual(
            iptools.selected_sections(self._Args(ip=True)),
            (True, False, False),
        )

    def test_ip_and_asn(self):
        self.assertEqual(
            iptools.selected_sections(self._Args(ip=True, asn=True)),
            (True, True, False),
        )


class SplitGlobalArgsTests(unittest.TestCase):
    def test_no_global_args(self):
        config_path, skips, no_skip, remaining = iptools.split_global_args(
            ["info", "8.8.8.8"]
        )
        self.assertIsNone(config_path)
        self.assertEqual(skips, [])
        self.assertFalse(no_skip)
        self.assertEqual(remaining, ["info", "8.8.8.8"])

    def test_config_space_form(self):
        config_path, _, _, remaining = iptools.split_global_args(
            ["--config", "/tmp/c", "info"]
        )
        self.assertEqual(config_path, "/tmp/c")
        self.assertEqual(remaining, ["info"])

    def test_config_equals_form(self):
        config_path, _, _, remaining = iptools.split_global_args(
            ["--config=/tmp/c", "info"]
        )
        self.assertEqual(config_path, "/tmp/c")
        self.assertEqual(remaining, ["info"])

    def test_repeated_skip(self):
        _, skips, _, remaining = iptools.split_global_args(
            ["--skip", "8.8.8.8", "--skip=AS15169", "expand", "1.1.1.0/30"]
        )
        self.assertEqual(skips, ["8.8.8.8", "AS15169"])
        self.assertEqual(remaining, ["expand", "1.1.1.0/30"])

    def test_no_skip_flag(self):
        _, _, no_skip, remaining = iptools.split_global_args(["--no-skip", "info", "x"])
        self.assertTrue(no_skip)
        self.assertEqual(remaining, ["info", "x"])


class SkipRulesTests(unittest.TestCase):
    def _rules(self, targets):
        return iptools.skip_rules(iptools.Config(skip_public_ip=False, skip_targets=targets))

    def test_classifies_targets(self):
        rules = self._rules(["8.8.8.8", "192.0.2.0/24", "AS15169"])
        self.assertTrue(rules.any_rules())
        self.assertTrue(rules.has_lookup_rules())
        self.assertIn(iptools.ipaddress.ip_address("8.8.8.8"), rules.ips)
        self.assertEqual([str(n) for n in rules.networks], ["192.0.2.0/24"])
        self.assertEqual(rules.asns, {"AS15169"})

    def test_empty_rules(self):
        rules = self._rules([])
        self.assertFalse(rules.any_rules())
        self.assertFalse(rules.has_lookup_rules())

    def test_ip_is_skipped_exact(self):
        rules = self._rules(["8.8.8.8"])
        self.assertTrue(iptools.ip_is_skipped("8.8.8.8", rules))
        self.assertFalse(iptools.ip_is_skipped("1.1.1.1", rules))

    def test_ip_is_skipped_within_network(self):
        rules = self._rules(["192.0.2.0/24"])
        self.assertTrue(iptools.ip_is_skipped("192.0.2.55", rules))
        self.assertFalse(iptools.ip_is_skipped("192.0.3.1", rules))

    def test_asn_is_skipped_multiple_origins(self):
        rules = self._rules(["AS1239"])
        # A Team Cymru ASN field can list multiple origins separated by spaces.
        self.assertTrue(iptools.asn_is_skipped("701 1239", rules))
        self.assertFalse(iptools.asn_is_skipped("701 702", rules))

    def test_network_is_skipped_contained(self):
        rules = self._rules(["192.0.2.0/24"])
        self.assertTrue(iptools.network_is_skipped("192.0.2.0/25", rules))
        self.assertFalse(iptools.network_is_skipped("192.0.0.0/16", rules))

    def test_filter_skipped_ips(self):
        rules = self._rules(["192.0.2.0/24"])
        self.assertEqual(
            iptools.filter_skipped_ips(["192.0.2.1", "1.1.1.1"], rules),
            ["1.1.1.1"],
        )

    def test_filter_skipped_asns(self):
        rules = self._rules(["AS15169"])
        self.assertEqual(
            iptools.filter_skipped_asns(["AS15169", "AS64500"], rules),
            ["AS64500"],
        )


class ConfigFileTests(unittest.TestCase):
    def _write(self, contents):
        handle = tempfile.NamedTemporaryFile(
            mode="w", suffix=".conf", delete=False, encoding="utf-8"
        )
        handle.write(contents)
        handle.close()
        self.addCleanup(os.unlink, handle.name)
        return handle.name

    def test_read_config_file(self):
        path = self._write(
            "skip_public_ip = true\n"
            "\n"
            "# a comment\n"
            "[skip]\n"
            "8.8.8.8\n"
            "192.0.2.0/24  ; inline comment\n"
            "AS15169\n"
        )
        loaded = iptools.read_config_file(path)
        self.assertIs(loaded.skip_public_ip, True)
        self.assertEqual(loaded.skip_targets, ["8.8.8.8", "192.0.2.0/24", "AS15169"])

    def test_load_config_later_file_overrides_bool(self):
        first = self._write("skip_public_ip = true\n[skip]\n8.8.8.8\n")
        second = self._write("skip_public_ip = false\n[skip]\nAS15169\n")
        config = iptools.load_config([first, second])
        # Later files override booleans; skip entries are cumulative.
        self.assertFalse(config.skip_public_ip)
        self.assertEqual(config.skip_targets, ["8.8.8.8", "AS15169"])

    def test_load_config_ignores_missing_paths(self):
        config = iptools.load_config(["/nonexistent/path/xyz.conf"])
        self.assertFalse(config.skip_public_ip)
        self.assertEqual(config.skip_targets, [])


class InfoAsnsTests(unittest.TestCase):
    def test_extracts_asn_from_payload(self):
        data = {"org": "AS15169 Google LLC", "ip": "8.8.8.8"}
        self.assertEqual(iptools.info_asns(data), ["AS15169"])


if __name__ == "__main__":
    unittest.main()
