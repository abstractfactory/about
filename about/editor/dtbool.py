
# import pigui.item
import about.item

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class Item(about.item.EditorItem):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        state = self.node.data.get('value')
        self.widget.checkbox.setChecked(state)
        self.widget.checkbox.stateChanged.connect(self.modified_event)

    def modified_event(self, state):
        self.event.emit(name='modified',
                        data=[True if state else False, self])


class Widget(QtWidgets.QWidget):
    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)

        checkbox = QtWidgets.QCheckBox()

        layout = QtWidgets.QHBoxLayout(self)
        layout.addWidget(checkbox)
        layout.setContentsMargins(*[0]*4)
        layout.setAlignment(QtCore.Qt.AlignRight)

        self.checkbox = checkbox


class Family(object):
    predicate = 'bool'
    ItemClass = Item
    WidgetClass = Widget


def register():
    about.item.EditorItem.register(Family)
