"""Entry-items represent inner Open Metadata files and folders"""

import piapp
piapp.setup_log()

import pifou.lib
import pigui.item
import pigui.service
import pigui.widgets.pyqt5.item

from PyQt5 import QtWidgets
from PyQt5 import QtCore
from PyQt5 import QtGui

import openmetadata as om

pull_method = om.pull


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


@pifou.lib.log
class EntryItem(pigui.widgets.pyqt5.item.TreeItem):
    """
    Parameters
        node        -- A Group or Dataset
        widget      -- Graphical representation or `node`

    """

    def __init__(self, node, widget, parent=None):
        super(EntryItem, self).__init__(node, widget)

        if hasattr(self.widget, 'setText'):
            widget.setText(self.name)

        if hasattr(widget, 'open_in_explorer'):
            widget.open_in_explorer.connect(self.open_in_explorer)

        widget.setProperty('type', self.node.path.suffix)

    def open_in_explorer(self):
        if self.node.iscollection:
            path = self.node.path.as_str
        else:
            path = self.node.path.parent.as_str
        pigui.service.open_in_explorer(path)

    @classmethod
    def from_node(cls, node, widget=None, parent=None):
        """
         ____
        |    |_______
        |            |
        |   __/_     |
        |    /       |
        |____________|

        Instantiate a EntryItem via Node

        """

        widget = widget or EntryWidget()
        item = EntryItem(node, widget)

        return item

    @property
    def children(self):
        """
         ______         ____
        |      |\      |    |_______
        |        |     |            |
        |        |  +  |            |
        |        |     |            |
        |________|     |____________|

        A group may return both Group and Dataset items

        """

        try:
            # It's important that the pull is lazy. That way,
            # when the entryitem has been modified, but not saved,
            # the user may switch to another item without loosing
            # the modified information.
            #
            # The alternative would be to temporarily store this
            # data within the item, rather than the metanode.
            pull_method(self.node,
                        lazy=True)  # Lazy will preserve edited
                                    # entrys that have not
                                    # yet been flushed.
        except om.error.Exists:
            self.log.warning("%r did not exist"
                             % self.node.path)
            # return

        if self.node.iscollection:
            for child in self.node:
                item = self.from_node(child)

                # Post-process
                item = self.postprocess.process(item)

                item.preprocess = self.preprocess.copy()
                item.postprocess = self.postprocess.copy()

                if item:
                    yield item
        else:
            if self.node.type is None:
                return

            editor = EditorItem.from_node(self.node, parent=self)

            # Post-process
            editor = self.postprocess.process(editor)

            if editor:
                yield editor

    def getdata(self, key=None):
        data = self._data.get(key)

        if data is None:
            try:
                pull_method(self.node, lazy=True)
            except om.error.Exists:
                pass

            data = self.node.value

        return data

    def hasdata(self, key):
        raise NotImplementedError
        has = key in self._data
        return has

    @property
    def name(self):
        if not self._name:
            self._name = self.node.name
        return self._name


class LocationWidget(EntryWidget):
    pass


class LocationItem(EntryItem):
    """Wrap om.Location in graphics"""

    @property
    def name(self):
        if not self._name:
            self._name = self.node.name
        return self._name


class EditorWidget(EntryWidget):
    pass


@pifou.lib.registry
class EditorItem(EntryItem):
    def __init__(self, *args, **kwargs):
        super(EditorItem, self).__init__(*args, **kwargs)
        self.widget.setProperty('metaeditor', True)

    # def init_widget(self, widget):
    #     super(EditorItem, self).init_widget(widget)

    #     dir_sequence = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_Return)
    #     dir_key = QtWidgets.QShortcut(dir_sequence, self)
    #     dir_key.activated.connect(self.flush)

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
