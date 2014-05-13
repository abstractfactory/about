
import about.item

from PyQt5 import QtWidgets


class Item(about.item.EditorItem):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        text = self.node.data['value']
        self.widget.setText(text)
        self.widget.textChanged.connect(self.modified_event)

    def modified_event(self, text):
        self.event.emit(name='modified',
                        data=[text, self])


class Widget(QtWidgets.QLineEdit):
    pass


class Family(object):
    predicate = 'string'
    ItemClass = Item
    WidgetClass = Widget


def register():
    about.item.EditorItem.register(Family)
