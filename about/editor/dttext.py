
import pigui.pyqt5.event
import pigui.pyqt5.widgets.delegate

from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Editor(pigui.pyqt5.widgets.delegate.BlankDelegate):
    def __init__(self, default, index, parent=None):
        super(Editor, self).__init__(index=index, parent=parent)
        self.index = index

        text = QtWidgets.QPlainTextEdit()
        text.setPlainText(unicode(default))
        text.textChanged.connect(self.data_changed_event)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(text)
        layout.setAlignment(QtCore.Qt.AlignRight)
        layout.setContentsMargins(0, 0, 0, 0)

        self.text = text

    def data_changed_event(self):
        event = pigui.pyqt5.event.DataEditedEvent(data=self.text.toPlainText(),
                                                  index=self.index)
        QtWidgets.QApplication.postEvent(self, event)
