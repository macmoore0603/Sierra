"""
Unit tests for KasaAgent helper methods (color conversion, device resolution).

These tests exercise pure logic that does not require network access or
real Kasa devices.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

BACKEND_DIR = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from kasa_agent import KasaAgent


@pytest.fixture
def agent():
    return KasaAgent()


class TestNameToHsv:
    """Verify the named-color → HSV conversion table."""

    @pytest.mark.parametrize(
        "name,expected_hue",
        [
            ("red", 0),
            ("green", 120),
            ("blue", 240),
            ("purple", 300),
            ("yellow", 60),
            ("cyan", 180),
            ("orange", 30),
        ],
    )
    def test_primary_colors(self, agent, name, expected_hue):
        h, s, v = agent.name_to_hsv(name)
        assert h == expected_hue
        assert s == 100
        assert v == 100

    def test_warm_white(self, agent):
        hsv = agent.name_to_hsv("warm")
        assert hsv is not None
        assert hsv[1] < 50, "warm white should have low saturation"

    def test_cool_white(self, agent):
        hsv = agent.name_to_hsv("cool")
        assert hsv is not None
        assert hsv[1] < 50

    def test_case_insensitive(self, agent):
        assert agent.name_to_hsv("RED") == agent.name_to_hsv("red")
        assert agent.name_to_hsv("  Blue  ") == agent.name_to_hsv("blue")

    def test_unknown_color_returns_none(self, agent):
        assert agent.name_to_hsv("chartreuse") is None
        assert agent.name_to_hsv("") is None


class TestDeviceResolution:
    """Verify _resolve_device looks up by IP and alias."""

    def test_resolve_by_ip(self, agent):
        mock_dev = MagicMock()
        agent.devices["192.168.1.100"] = mock_dev
        assert agent._resolve_device("192.168.1.100") is mock_dev

    def test_resolve_by_alias(self, agent):
        mock_dev = MagicMock()
        mock_dev.alias = "Kitchen Light"
        agent.devices["10.0.0.5"] = mock_dev
        assert agent._resolve_device("Kitchen Light") is mock_dev

    def test_resolve_alias_case_insensitive(self, agent):
        mock_dev = MagicMock()
        mock_dev.alias = "Bedroom Lamp"
        agent.devices["10.0.0.6"] = mock_dev
        assert agent._resolve_device("bedroom lamp") is mock_dev

    def test_resolve_unknown_returns_none(self, agent):
        assert agent._resolve_device("no-such-device") is None


class TestKasaAgentInit:
    def test_default_init(self):
        agent = KasaAgent()
        assert agent.devices == {}
        assert agent.known_devices_config == []

    def test_init_with_known_devices(self):
        config = [{"ip": "1.2.3.4", "alias": "Test"}]
        agent = KasaAgent(known_devices=config)
        assert agent.known_devices_config == config
