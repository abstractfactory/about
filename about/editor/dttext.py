
# import pigui.item
import about.item

# from PyQt5 import QtCore
from PyQt5 import QtWidgets


class Item(about.item.EditorItem):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        text = self.node.data.get('value')
        self.widget.setPlainText(text)
        self.widget.textChanged.connect(self.modified_event)

    def modified_event(self):
        text = self.widget.toPlainText()
        self.event.emit(name='modified',
                        data=[text, self])


class Widget(QtWidgets.QPlainTextEdit):
    pass


class Family(object):
    predicate = 'text'
    ItemClass = Item
    WidgetClass = Widget


def register():
    about.item.EditorItem.register(Family)
