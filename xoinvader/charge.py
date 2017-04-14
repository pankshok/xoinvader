"""Game weapon charge classes."""


import logging
import curses

from xoinvader import application
from xoinvader.common import Settings, get_json_config
from xoinvader.render import Renderable
from xoinvader.utils import Point, Surface


CONFIG = get_json_config(Settings.path.config.charges)
LOG = logging.getLogger(__name__)


# pylint: disable=too-many-arguments
class WeaponCharge(Renderable):
    """Weapon charge representation.

    Separate renderable object that updates and renders as others
    in main loop. Must register/deregister itself via state's
    add/remove methods.
    """

    def __init__(self, pos, image, damage=0, radius=0, dx=0, dy=0):
        self._pos = pos
        self._image = image
        self._type = self.__class__.__name__
        application.get_current().state.add(self)

        self._damage = damage
        self._radius = radius
        # TODO: [object-movement]
        # Generalize update to support dx
        self._dx = dx
        self._dy = dy

    def get_render_data(self):
        return ([self._pos], self._image.get_image())

    def remove_obsolete(self, pos):
        LOG.debug("%s remove obsolete.", self._type)
        application.get_current().state.remove(self)

    def update(self):
        """Update coords."""

        self._pos += Point(self._dx, self._dy)


# TODO: Implement hitscan behaviour
# pylint: disable=useless-super-delegation
class Hitscan(WeaponCharge):
    """Hitscan weapon charge hits target immediately.

    Can pierce enemies?
    """

    def __init__(self, pos, image, **kwargs):
        super(Hitscan, self).__init__(pos, image, **kwargs)


class Projectile(WeaponCharge):
    """Projectile weapon has generic physics of movement."""

    def __init__(self, pos, image, **kwargs):
        super(Projectile, self).__init__(pos, image, **kwargs)


# TODO: write template documentation for charges and weapons
class BasicPlasmaCannon(Projectile):
    """Small damage, no radius."""

    def __init__(self, pos):
        super(BasicPlasmaCannon, self).__init__(
            pos, Surface(["^"], style=[[curses.A_BOLD]]),
            **CONFIG[self.__class__.__name__])


class EBasicPlasmaCannon(Projectile):
    """Enemy plasma cannon."""

    def __init__(self, pos):
        super(EBasicPlasmaCannon, self).__init__(
            pos, Surface([":"], style=[[curses.A_BOLD]]),
            **CONFIG[self.__class__.__name__])


class BasicLaserCharge(Projectile):
    """Laser. Quite fast but cannot pierce enemies."""

    def __init__(self, pos):
        super(BasicLaserCharge, self).__init__(
            pos, Surface(["|"], style=[[curses.A_BOLD]]),
            **CONFIG[self.__class__.__name__])


class BasicUnguidedMissile(Projectile):
    """Unguided missile with medium damage and small radius."""

    def __init__(self, pos):
        super(BasicUnguidedMissile, self).__init__(
            pos, Surface([
                "^",
                "|",
                "*"
            ], style=[[curses.A_BOLD] for _ in range(3)]),
            **CONFIG[self.__class__.__name__])
