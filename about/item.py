"""Entry-items represent inner Open Metadata files and folders"""

import pifou.lib

import pigui.item
import pigui.service
import pigui.widgets.pyqt5.item

from PyQt5 import QtWidgets


@pifou.lib.log
class EntryItem(pigui.widgets.pyqt5.item.TreeItem):
    """
    Parameters
        node        -- A Group or Dataset
        widget      -- Graphical representation or `node`

    """

    @property
    def name(self):
        if not self._name:
            self._name = self.node.path.name
        return self._name

    def __init__(self, node, widget, parent=None):
        super(EntryItem, self).__init__(node, widget)

        if hasattr(widget, 'open_in_explorer'):
            widget.open_in_explorer.connect(self.open_in_explorer)

        widget.setProperty('type', self.node.path.suffix)

    def open_in_explorer(self):
        path = self.node.path.as_str
        pigui.service.open_in_explorer(path)

    @classmethod
    def from_node(cls, node, widget=None, parent=None):
        widget = widget or EntryWidget()
        item = EntryItem(node, widget)

        return item


class EntryWidget(pigui.widgets.pyqt5.item.ItemWidget):
    def __init__(self, *args, **kwargs):
        super(EntryWidget, self).__init__(*args, **kwargs)
        self.setCheckable(True)

        self.open_in_explorer_action = None

        # Signals
        self.open_in_explorer = pifou.signal.Signal()

        self.init_actions()

    def init_actions(self):
        # QActions transmit their checked-state, but we won't
        # make use of it in Item. We use lambda to silence that.
        oie_signal = lambda state: self.open_in_explorer.emit()

        oie_action = QtWidgets.QAction("&Open in Explorer", self,
                                       statusTip="Open in Explorer",
                                       triggered=oie_signal)

        self.open_in_explorer_action = oie_action

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        for action in (self.open_in_explorer_action,):

            if not action:
                continue

            menu.addAction(action)
        menu.exec_(event.globalPos())


class LocationItem(EntryItem):
    """Wrap om.Location in graphics"""


class LocationWidget(EntryWidget):
    pass


class EditorWidget(EntryWidget):
    pass


@pifou.lib.registry
class EditorItem(EntryItem):
    def __init__(self, *args, **kwargs):
        super(EditorItem, self).__init__(*args, **kwargs)
        self.widget.setProperty('metaeditor', True)

    @classmethod
    def from_node(self, node, parent=None):
        family = self.get_registered(node.path.suffix)

        widget_class = family.WidgetClass
        item_class = family.ItemClass

        if not widget_class:
            raise ValueError("No Widget-class provided in family: %r" % family)

        item = item_class(node, widget_class(), parent)

        return item


class EditorFamily(object):
    predicate = None
    ItemClass = EditorItem
    WidgetClass = EditorWidget


def register():
    EditorItem.register(EditorFamily)


register()
