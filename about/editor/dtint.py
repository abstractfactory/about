
# import pigui.item
import piapp.about.entryitem

from PyQt5 import QtWidgets


class IntItem(piapp.about.entryitem.EditorItem):
    def __init__(self, *args, **kwargs):
        super(IntItem, self).__init__(*args, **kwargs)

        value = self.getdata()
        self.widget.setValue(value)
        self.widget.valueChanged.connect(self.modified_event)

    def modified_event(self, value):
        self.event.emit(name='modified',
                        data=[value, self])


class IntWidget(QtWidgets.QSpinBox):
    def __init__(self, *args, **kwargs):
        super(IntWidget, self).__init__(*args, **kwargs)
        self.setRange(-99999999, 99999999)


class IntFamily(object):
    predicate = 'int'
    ItemClass = IntItem
    WidgetClass = IntWidget


def register():
    piapp.about.entryitem.EditorItem.register(IntFamily)
