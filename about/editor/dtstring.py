
import pigui.pyqt5.event
import pigui.pyqt5.widgets.item

from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Editor(pigui.pyqt5.widgets.item.BlankItem):
    def __init__(self, default, index, parent=None):
        super(Editor, self).__init__(index=index, parent=parent)
        self.index = index

        lineedit = QtWidgets.QLineEdit()
        lineedit.setText(unicode(default))
        lineedit.textChanged.connect(self.data_changed_event)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(lineedit)
        layout.setAlignment(QtCore.Qt.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)

        self.lineedit = lineedit

    def data_changed_event(self, text):
        event = pigui.pyqt5.event.DataEditedEvent(data=self.lineedit.text(),
                                                  index=self.index)
        QtWidgets.QApplication.postEvent(self, event)
