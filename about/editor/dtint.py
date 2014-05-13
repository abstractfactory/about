
# import pigui.item
import about.item

from PyQt5 import QtWidgets


class Item(about.item.EditorItem):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        value = self.node.data.get('value')
        self.widget.setValue(value)
        self.widget.valueChanged.connect(self.modified_event)

    def modified_event(self, value):
        self.event.emit(name='modified',
                        data=[value, self])


class Widget(QtWidgets.QSpinBox):
    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        self.setRange(-99999999, 99999999)


class Family(object):
    predicate = 'int'
    ItemClass = Item
    WidgetClass = Widget


def register():
    about.item.EditorItem.register(Family)
