
import pigui.pyqt5.event
import pigui.pyqt5.widgets.delegate

from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Editor(pigui.pyqt5.widgets.delegate.BlankDelegate):
    """If no editor is available for an delegate

    Arguments:
        ext     -- The extension for which there is no editor
        index   -- Index of parent model-delegate
        parent  -- Parent widget-delegate

    """

    def __init__(self, ext, index, parent=None):
        super(Editor, self).__init__(index=index, parent=parent)
        self.index = index

        label = QtWidgets.QLabel('No editor for type "{}"'.format(ext))
        label.setObjectName('Label')

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(label)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setAlignment(QtCore.Qt.AlignCenter)
