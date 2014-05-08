
# import pigui.item
import piapp.about.entryitem

from PyQt5 import QtWidgets


class StringItem(piapp.about.entryitem.EditorItem):
    def __init__(self, *args, **kwargs):
        super(StringItem, self).__init__(*args, **kwargs)

        text = self.getdata()
        self.widget.setText(text)
        self.widget.textChanged.connect(self.modified_event)

    def modified_event(self, text):
        self.event.emit(name='modified',
                        data=[text, self])


class StringWidget(QtWidgets.QLineEdit):
    pass


class StringFamily(object):
    predicate = 'string'
    ItemClass = StringItem
    WidgetClass = StringWidget


def register():
    piapp.about.entryitem.EditorItem.register(StringFamily)
