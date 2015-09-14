# -*- coding: utf-8 -*-
""" Graphical user interface widgets."""

#TODO: make working with styles pretty
from xoinvader.curses_utils import style as Style
from xoinvader.render import Renderable
from xoinvader.utils import Surface


class TextWidget(Renderable):
    """Simple text widget.

    :param pos: widget's global position
    :type pos: `xoinvader.utils.Point`

    :param text: contained text
    :type text: string

    .. note:: add [ [style], ...] support

    :param style: curses style for text
    :type style: integer(curses style)
    """

    render_priority = 1

    def __init__(self, pos, text, style=None):
        self._pos = pos
        self._text = text
        self._style = style
        self._image = self._make_image()

    def _make_image(self):
        """Make Surface object from text and style.

        :return: Surface instance
        :rtype: `xoinvader.utils.Surface`
        """
        _style = self._style or Style.gui["normal"]
        return Surface([[ch for ch in self._text]],
                       [[_style for _ in range(len(self._text))]])

    def update(self, text=None, style=None):
        """Obtain (or not) new data and refresh image.

        :param text: new text
        :type: string

        :param style: new style
        :type: integer(curses style)
        """
        if text:
            self._text = text
        if style:
            self._style = style
        if text or style:
            self._image = self._make_image

    def get_render_data(self):
        return [self._pos], self._image.get_image()


class MenuItemWidget(TextWidget):
    """Selectable menu item widget.

    :param pos: widget's global position
    :type pos: `xoinvader.utils.Point`

    :param text: contained text
    :type text: string

    :param template: left and right markers
    :type template: tuple of two strings

    .. note:: add [ [style] ... ] support

    :param style: curses style for text
    :type style: integer(curses style)
    """

    render_priority = 1

    def __init__(self, pos, text, template=("* ", " *"), style=None):
        self._left = template[0]
        self._right = template[1]
        self._selected = False

        super(MenuItemWidget, self).__init__(pos, text, style)

    def _make_image(self):
        """Make Surface object from text, markers and style.

        :return: Surface instance
        :rtype: `xoinvader.utils.Surface`
        """
        _style = self._style or Style.gui["yellow"]
        if self._selected:
            _full_text = "".join([self._left, self._text, self._right])
        else:
            _full_text = self._text

        return Surface([[ch for ch in _full_text]],
                       [[_style for _ in range(len(_full_text))]])

    def toggle_select(self):
        """Draw or not selector characters."""
        self._selected = not self._selected

    def select(self):
        """Select and refresh image."""
        self._selected = True
        self._image = self._make_image()

    def deselect(self):
        """Deselect and refresh image."""
        self._selected = False
        self._image = self._make_image()

    @property
    def selected(self):
        """Shows is item selected or not.

        .. warning:: Complete menu workflow.

        :getter: yes
        :setter: no
        :type: boolean
        """
        return self._selected

    def get_render_data(self):
        return [self._pos], self._image.get_image()


class WeaponWidget(Renderable):
    """Widget for displaying weapon information.


    """

    render_priority = 1

    def __init__(self, pos, get_data):
        self._pos = pos
        self._get_data = get_data
        self._data = self._get_data()
        self._image = self._make_image()

    def _make_image(self):
        """Return Surface object."""
        return Surface([[ch for ch in self._data]],
                       [[Style.gui["yellow"] for _ in range(len(self._data))]])

    def update(self):
        """Obtain new data and refresh image."""
        self._data = self._get_data()
        self._image = self._make_image()

    def get_render_data(self):
        """Return render specific data."""
        return [self._pos], self._image.get_image()


class Bar(Renderable):
    """
    Progress bar widget.

    :param pos: Bar's global position
    :type pos: `xoinvader.utils.Point`

    :param prefix: text before the bar
    :type prefix: string

    :param postfix: text after the bar
    :type postfix: string

    :param left: left edge of the bar
    :type left: string

    :param right: right edge of the bar
    :type right: string

    :param marker: symbol that fills the bar
    :type marker: string

    :param marker_style: curses style for marker (passes to render)
    :type marker_style: integer(curses style)

    :param empty: symbols that fills empty bar space (without marker)
    :type empty: string

    :param empty_style: curses style for empty marker (passes to render)
    :type emplty_style: integer(curses style)

    :param count: number of markers in the bar
    :type count: integer

    :param maxval: max value of displayed parameter (affects the accuracy)
    :type maxval: integer

    :param general_style: style of other characters(prefix, postfix, etc)
    :type general_style: integer(curses style)

    :param stylemap: mapping of compare functions and integers to curses style
    :type stylemap: dict(function, integer(curses style)

    :param callback: calls if not None to get new percentage value
    :type callback: function
    """

    render_priority = 1

    def __init__(self, pos,
                 prefix=u"", postfix=u"",
                 left=u"[", right=u"]",
                 marker=u"█", marker_style=None,
                 empty=u"-", empty_style=None,
                 count=10, maxval=100,
                 general_style=None,
                 stylemap=None, callback=None):

        self._pos = pos
        self._prefix = prefix
        self._postfix = postfix
        self._left = left
        self._right = right
        self._marker = marker
        self._marker_style = marker_style
        self._empty = empty
        self._empty_style = empty_style
        self._count = count
        self._maxval = maxval
        self._general_style = general_style
        self._stylemap = stylemap
        self._callback = callback

        self._template = u"".join([str(val) for val in
                                  [self._prefix, self._left, "{blocks}",
                                   self._right, self._postfix]])

        self._current_count = self._count
        self._image = None
        self._update_image()

    def _update_current_count(self, val):
        """Normalize current percentage and update count of marker blocks

        :param val: """
        self._current_count = int(round(val * self._count / self._maxval))

    def _style(self, val):
        """Return style in depend on percentage."""
        for cmp_func, bar_style in self._stylemap.items():
            if cmp_func(val):
                return bar_style
        return None

    def _update_image(self):
        """Update image in depend on persentage."""
        left = self._marker * self._current_count
        right = self._empty * (self._count - self._current_count)
        bar = self._template.format(blocks=left + right)
        image = []
        for char in bar:
            if char == self._marker:
                image.append((char, self._marker_style))
            else:
                image.append((char, self._general_style))
        self._image = Surface([[ch[0] for ch in image]],
                              [[st[1] for st in image]])

    def update(self, val=None):
        """Update bar if there's need for it."""
        if self._callback:
            val = self._callback()

        if val is None:
            raise ValueError("val = None, what to do?")

        self._marker_style = self._style(val)
        self._update_current_count(val)
        self._update_image()

    def get_render_data(self):
        return [self._pos], self._image.get_image()
