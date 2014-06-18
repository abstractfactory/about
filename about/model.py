# standard library
import os

# pifou library
import pifou.om
import pifou.lib

# pigui library
import pigui.pyqt5.model

# pigui dependency
import openmetadata
from PyQt5 import QtCore

# local library
# import about.key

# Dev-temp
openmetadata.setup_log()


class Item(pigui.pyqt5.model.ModelItem):
    def data(self, key):
        value = super(Item, self).data(key)

        if not value:
            if key == 'path':
                node = self.data('node')
                value = node.path.as_str

            if key == 'suffix':
                node = self.data('node')
                value = node.path.suffix

        return value


@pifou.lib.log
class Model(pigui.pyqt5.model.Model):
    error = QtCore.pyqtSignal(Exception)
    flushed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.save_queue = set()

    def setup(self, location):
        node = pifou.om.Location(location)
        root = self.create_item({'type': 'om',
                                 'node': node,
                                 'display': node.path.name})
        self.root_item = root
        self.model_reset.emit()

    def flush(self):
        self.flushed.emit()

    def create_item(self, data, parent=None):
        item = Item(data, parent)
        self.register_item(item)
        return item

    def add_entry(self, name, parent, group=False):
        model_parent = self.item(parent)
        entry_parent = self.data(parent, 'node')

        if not '.' in name:
            name += '.string'  # Default to string

        entry = pifou.om.Entry(name, parent=entry_parent)

        # Physically write to disk

        self.add_item({'type': 'om',
                       'node': entry,
                       'display': entry.path.name},
                      parent=model_parent)

    def pull(self, index):
        node = self.data(index, 'node')

        try:
            pifou.om.pull(node)
        except pifou.om.error.Exists:
            pass

        model_parent = self.item(index)

        if node.isparent:
            for child in node:
                self.create_item({'type': 'om',
                                  'node': child,
                                  'display': child.path.name},
                                 parent=model_parent)
        else:
            self.create_item({'type': 'om-editor',
                              'node': node,
                              'default': node.value},
                             parent=model_parent)

        super(Model, self).pull(index)

    def set_data(self, index, key, value):
        if key == pigui.pyqt5.model.Value:
            self.save_queue.add(index)

        if key == pigui.pyqt5.model.Display:
            path = self.data(index, 'path')
            suffix = self.data(index, 'suffix')

            basename = value
            suffix = suffix

            if suffix:
                basename += '.' + suffix

            dirname = os.path.dirname(path)

            old_path = path
            new_path = os.path.join(dirname, basename)

            try:
                os.rename(old_path, new_path)
            except OSError as e:
                self.log.error(str(e))
                return self.error.emit(e)

        super(Model, self).set_data(index, key, value)
