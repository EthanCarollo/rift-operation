"""Tests for the new 3-HP battle configuration with new combos."""
import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.Core.Config import Config


class TestConfigAttacks:
    """Tests for new attack configuration."""

    def test_attack_shield_exists(self):
        """SHIELD attack should be BOUCLIER."""
        assert Config.Attack.SHIELD == "BOUCLIER"

    def test_attack_rain_exists(self):
        """RAIN attack should be PLUIE."""
        assert Config.Attack.RAIN == "PLUIE"

    def test_attack_moon_exists(self):
        """MOON attack should be LUNE."""
        assert Config.Attack.MOON == "LUNE"


class TestConfigCounters:
    """Tests for new counter configuration."""

    def test_counter_sword_exists(self):
        """SWORD counter should be 'sword'."""
        assert Config.Counter.SWORD == "sword"

    def test_counter_umbrella_exists(self):
        """UMBRELLA counter should be 'umbrella'."""
        assert Config.Counter.UMBRELLA == "umbrella"

    def test_counter_sun_exists(self):
        """SUN counter should be 'sun'."""
        assert Config.Counter.SUN == "sun"


class TestAttackToCounterMapping:
    """Tests for attack-to-counter mapping (the combos)."""

    def test_shield_countered_by_sword(self):
        """Épée > Bouclier: SHIELD should be countered by sword."""
        assert Config.ATTACK_TO_COUNTER_LABEL[Config.Attack.SHIELD] == Config.Counter.SWORD

    def test_rain_countered_by_umbrella(self):
        """Parapluie > Pluie: RAIN should be countered by umbrella."""
        assert Config.ATTACK_TO_COUNTER_LABEL[Config.Attack.RAIN] == Config.Counter.UMBRELLA

    def test_moon_countered_by_sun(self):
        """Soleil > Lune: MOON should be countered by sun."""
        assert Config.ATTACK_TO_COUNTER_LABEL[Config.Attack.MOON] == Config.Counter.SUN

    def test_mapping_has_exactly_three_entries(self):
        """Mapping should have exactly 3 entries for 3 HP."""
        assert len(Config.ATTACK_TO_COUNTER_LABEL) == 3


class TestGetNextAttack:
    """Tests for HP-based attack progression."""

    def test_hp_3_returns_shield(self):
        """HP 3 should return SHIELD (first attack)."""
        assert Config.get_next_attack(3) == Config.Attack.SHIELD

    def test_hp_2_returns_rain(self):
        """HP 2 should return RAIN (second attack)."""
        assert Config.get_next_attack(2) == Config.Attack.RAIN

    def test_hp_1_returns_moon(self):
        """HP 1 should return MOON (final attack)."""
        assert Config.get_next_attack(1) == Config.Attack.MOON

    def test_hp_0_returns_none(self):
        """HP 0 should return None (battle over)."""
        assert Config.get_next_attack(0) is None

    def test_hp_4_returns_none(self):
        """HP 4 (invalid) should return None."""
        assert Config.get_next_attack(4) is None

    def test_hp_5_returns_none(self):
        """HP 5 (old system) should return None."""
        assert Config.get_next_attack(5) is None


class TestPromptMapping:
    """Tests for prompt mappings."""

    def test_sword_has_prompt(self):
        """sword should have a generation prompt."""
        assert Config.PROMPT_MAPPING.get("sword") is not None
        assert "sword" in Config.PROMPT_MAPPING["sword"].lower()

    def test_umbrella_has_prompt(self):
        """umbrella should have a generation prompt."""
        assert Config.PROMPT_MAPPING.get("umbrella") is not None
        assert "umbrella" in Config.PROMPT_MAPPING["umbrella"].lower()

    def test_sun_has_prompt(self):
        """sun should have a generation prompt."""
        assert Config.PROMPT_MAPPING.get("sun") is not None
        assert "sun" in Config.PROMPT_MAPPING["sun"].lower()

    def test_empty_has_no_prompt(self):
        """empty should skip generation (None)."""
        assert Config.PROMPT_MAPPING.get("empty") is None

    def test_bullshit_has_no_prompt(self):
        """bullshit should skip generation (None)."""
        assert Config.PROMPT_MAPPING.get("bullshit") is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
