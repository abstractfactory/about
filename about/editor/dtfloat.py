
# import pigui.item
import piapp.about.entryitem

from PyQt5 import QtWidgets


class FloatItem(piapp.about.entryitem.EditorItem):
    def __init__(self, *args, **kwargs):
        super(FloatItem, self).__init__(*args, **kwargs)

        value = self.getdata()
        self.widget.setRange(-99999999, 99999999)
        self.widget.setValue(value)
        self.widget.valueChanged.connect(self.modified_event)

    def modified_event(self, value):
        self.event.emit(name='modified',
                        data=[value, self])


class FloatWidget(QtWidgets.QDoubleSpinBox):
    pass


class FloatFamily(object):
    predicate = 'float'
    ItemClass = FloatItem
    WidgetClass = FloatWidget


def register():
    piapp.about.entryitem.EditorItem.register(FloatFamily)
