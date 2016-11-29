import pytest

import xoinvader
from xoinvader import weapon


@pytest.mark.skip
def test_weapon(monkeypatch):
    monkeypatch.setattr(weapon, "CONFIG", {})
    monkeypatch.setattr(weapon, "Mixer", xoinvader.sound.get_mixer)

    # pytest.raises(KeyError, lambda:
    weapon.Weapon(ammo=10, max_ammo=10, cooldown=0.5, damage=1, radius=1, dy=1)
