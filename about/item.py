"""Entry-items represent inner Open Metadata files and folders"""

# pigui library
import pigui.pyqt5.event
import pigui.pyqt5.widgets.item

# pigui dependencies
from PyQt5 import QtWidgets


class EntryItem(pigui.pyqt5.widgets.item.TreeItem):
    """Append context-menu"""

    def action_event(self, state):
        action = self.sender()
        label = action.text()

        if label == "Open in Explorer":
            event = pigui.pyqt5.event.OpenInExplorerEvent(index=self.index)
            QtWidgets.QApplication.postEvent(self, event)

        elif label == "Recycle":
            event = pigui.pyqt5.event.RemoveItemEvent(index=self.index)
            QtWidgets.QApplication.postEvent(self, event)

    def contextMenuEvent(self, event):
        menu = QtWidgets.QMenu(self)

        for label in ("Open in Explorer",
                      "Recycle"):
            action = QtWidgets.QAction(label,
                                       self,
                                       triggered=self.action_event)
            menu.addAction(action)

        menu.exec_(event.globalPos())

    def mouseDoubleClickEvent(self, event):
        event = pigui.pyqt5.event.EditItemEvent(index=self.index)
        QtWidgets.QApplication.postEvent(self, event)
