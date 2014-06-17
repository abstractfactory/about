
import pigui.pyqt5.event
import pigui.pyqt5.widgets.item

from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Editor(pigui.pyqt5.widgets.item.BlankItem):
    @property
    def data(self):
        return self.checkbox.isChecked()

    def __init__(self, default, index, parent=None):
        super(Editor, self).__init__(index=index, parent=parent)
        self.index = index

        checkbox = QtWidgets.QCheckBox()
        checkbox.setChecked(default or False)
        checkbox.stateChanged.connect(self.data_changed_event)

        label = QtWidgets.QLabel('True' if default else 'False')
        label.setObjectName('Label')

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(label)
        layout.addWidget(checkbox)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignRight)

        self.setProperty('type', 'bool')

        self.checkbox = checkbox

    def data_changed_event(self, state):
        label = self.findChild(QtWidgets.QLabel, 'Label')
        label.setText('True' if state else 'False')
        event = pigui.pyqt5.event.DataEditedEvent(data=self.data,
                                                  index=self.index)
        QtWidgets.QApplication.postEvent(self, event)
