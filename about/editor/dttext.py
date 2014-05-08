
# import pigui.item
import piapp.about.entryitem

# from PyQt5 import QtCore
from PyQt5 import QtWidgets


class TextItem(piapp.about.entryitem.EditorItem):
    def __init__(self, *args, **kwargs):
        super(TextItem, self).__init__(*args, **kwargs)

        text = self.getdata()
        self.widget.setPlainText(text)
        self.widget.textChanged.connect(self.modified_event)

    def modified_event(self):
        text = self.widget.toPlainText()
        self.event.emit(name='modified',
                        data=[text, self])


class TextWidget(QtWidgets.QPlainTextEdit):
    pass


class TextFamily(object):
    predicate = 'text'
    ItemClass = TextItem
    WidgetClass = TextWidget


def register():
    piapp.about.entryitem.EditorItem.register(TextFamily)
