
# import pigui.item
import about.item

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class Item(about.item.EditorItem):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)

        # date = self.getdata()
        # self.widget.set(date)
        # self.widget.setTime(date)
        self.widget.dateChanged.connect(self.modified_event)

    def modified_event(self, date):
        pass
        # print " changed to: %r" % date
        # self.event.emit(name='modified',
        #                 data=[True if date else False, self])


class Widget(QtWidgets.QTimeEdit):
    def __init__(self, *args, **kwargs):
        super(Widget, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)


class Family(object):
    predicate = 'date'
    ItemClass = Item
    WidgetClass = Widget


def register():
    about.item.EditorItem.register(Family)
