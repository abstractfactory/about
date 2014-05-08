
# import pigui.item
import piapp.about.entryitem

from PyQt5 import QtWidgets
from PyQt5 import QtCore


class DateItem(piapp.about.entryitem.EditorItem):
    def __init__(self, *args, **kwargs):
        super(DateItem, self).__init__(*args, **kwargs)

        # date = self.getdata()
        # self.widget.setDate(date)
        # self.widget.setTime(date)
        self.widget.dateChanged.connect(self.modified_event)

    def modified_event(self, date):
        pass
        # print "Date changed to: %r" % date
        # self.event.emit(name='modified',
        #                 data=[True if date else False, self])


class DateWidget(QtWidgets.QDateTimeEdit):
    def __init__(self, *args, **kwargs):
        super(DateWidget, self).__init__(*args, **kwargs)
        self.setAttribute(QtCore.Qt.WA_StyledBackground)


class DateFamily(object):
    predicate = 'date'
    ItemClass = DateItem
    WidgetClass = DateWidget


def register():
    piapp.about.entryitem.EditorItem.register(DateFamily)
