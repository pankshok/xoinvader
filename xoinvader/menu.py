"""MainMenuState-related input and event handlers."""

from xoinvader import application
from xoinvader.gui import (
    MenuItemContainer,
    MenuItemWidget,
    PopUpNotificationWidget,
    TextCallbackWidget,
    TextWidget,
)
from xoinvader.handlers import EventHandler
from xoinvader.keys import KEY
from xoinvader.state import State
from xoinvader.utils import Point


class MainMenuState(State):

    def __init__(self, owner):
        super(MainMenuState, self).__init__(owner)
        self._screen = owner.screen
        self._owner = owner
        self._actor = None  # Should be some of Menu instances?

        self.add(TextWidget(Point(4, 4), "Pause"))
        self._items = MenuItemContainer([
            MenuItemWidget(
                Point(10, 10), "Continue",
                template=("=> ", ""),
                action=lambda: application.get_current().trigger_state("InGameState")),
            MenuItemWidget(
                Point(10, 11), "Quit",
                template=("=> ", ""),
                action=application.get_current().stop),
        ])
        self._items.select(0)
        self.add(self._items)

        self._events = EventHandler(self, {
            KEY.ESCAPE: lambda: application.get_current().trigger_state("InGameState"),
            KEY.N: lambda: self.notify("This is test notification"),
            KEY.W: self._items.prev,
            KEY.S: self._items.next,
            KEY.F: self._items.do_action,
        })

    def notify(self, text, pos=Point(15, 15)):
        self.add(
            PopUpNotificationWidget(
                pos, text,
                callback=lambda w: self.remove(w)))

    def events(self):
        self._events.handle()


class GameOverState(State):

    def __init__(self, owner):
        super(GameOverState, self).__init__(owner)
        self._screen = owner.screen
        self._actor = None

        self._score = "Your score: {0}"

        self._objects = [
            TextWidget(Point(4, 4), "Your soul completely lost this time"),
            TextCallbackWidget(Point(4, 5), self.score_callback),
            MenuItemWidget(Point(10, 10), "I agree"),
            MenuItemWidget(Point(10, 11), "No, I want more")
        ]
        self._objects[2].select()
        self._events = EventHandler(self, {
            KEY.ESCAPE: application.get_current().stop,
            # KEY.ENTER: exit_game_command,
        })

    def score_callback(self):
        return self._score

    def trigger(self, score):
        """Trigger the state and pass the score info to it.

        :param int score: last player score
        """

        self._score = self._score.format(score)

    def events(self):
        self._events.handle()
