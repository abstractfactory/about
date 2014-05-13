
# import pigui.item
import about.item

from PyQt5 import QtWidgets


class Item(about.item.EditorItem):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        value = self.node.data.get('value')
        self.widget.setRange(-99999999, 99999999)
        self.widget.setValue(value)
        self.widget.valueChanged.connect(self.modified_event)

    def modified_event(self, value):
        self.event.emit(name='modified',
                        data=[value, self])


class Widget(QtWidgets.QDoubleSpinBox):
    pass


class Family(object):
    predicate = 'float'
    ItemClass = Item
    WidgetClass = Widget


def register():
    about.item.EditorItem.register(Family)
