
from PyQt5 import QtWidgets

import pigui.pyqt5.event
import pigui.pyqt5.widgets.delegate

from PyQt5 import QtCore


class Editor(pigui.pyqt5.widgets.delegate.BlankDelegate):
    def __init__(self, default, index, parent=None):
        super(Editor, self).__init__(index=index, parent=parent)
        self.index = index

        spinbox = QtWidgets.QDoubleSpinBox()
        spinbox.setValue(default)
        spinbox.setRange(-99999999, 99999999)
        spinbox.valueChanged.connect(self.data_changed_event)

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(spinbox)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignRight)

        self.spinbox = spinbox

    def data_changed_event(self, state):
        event = pigui.pyqt5.event.DataEditedEvent(
            data=self.spinbox.value(),
            index=self.index)
        QtWidgets.QApplication.postEvent(self, event)
