"""Tests for peertube_to_amb.licence_map."""

import pytest

from peertube_to_amb.licence_map import LICENCE_MAP, get_licence_uri


class TestGetLicenceUri:
    """Test PeerTube licence ID to Creative Commons URI mapping."""

    def test_licence_1_maps_to_cc_by(self):
        result = get_licence_uri("1")

        assert result == "https://creativecommons.org/licenses/by/4.0/"

    def test_licence_2_maps_to_cc_by_sa(self):
        result = get_licence_uri("2")

        assert result == "https://creativecommons.org/licenses/by-sa/4.0/"

    def test_licence_3_maps_to_cc_by_nd(self):
        result = get_licence_uri("3")

        assert result == "https://creativecommons.org/licenses/by-nd/4.0/"

    def test_licence_4_maps_to_cc_by_nc(self):
        result = get_licence_uri("4")

        assert result == "https://creativecommons.org/licenses/by-nc/4.0/"

    def test_licence_5_maps_to_cc_by_nc_sa(self):
        result = get_licence_uri("5")

        assert result == "https://creativecommons.org/licenses/by-nc-sa/4.0/"

    def test_licence_6_maps_to_cc_by_nc_nd(self):
        result = get_licence_uri("6")

        assert result == "https://creativecommons.org/licenses/by-nc-nd/4.0/"

    def test_licence_7_maps_to_cc0(self):
        result = get_licence_uri("7")

        assert result == "https://creativecommons.org/publicdomain/zero/1.0/"

    def test_unknown_identifier_returns_none(self):
        result = get_licence_uri("999")

        assert result is None

    def test_empty_string_returns_none(self):
        result = get_licence_uri("")

        assert result is None


class TestLicenceMapKeys:
    """Verify that licence map identifiers are strings, not integers."""

    def test_all_keys_are_strings(self):
        assert all(isinstance(k, str) for k in LICENCE_MAP.keys())

    def test_integer_key_does_not_match(self):
        result = get_licence_uri(1)  # type: ignore[arg-type]

        assert result is None
