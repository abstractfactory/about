# standard library
import os

# pifou library
import pifou.om
import pifou.lib

# pigui library
import pigui.pyqt5.model

# pigui dependency
from PyQt5 import QtCore


class Item(pigui.pyqt5.model.ModelItem):
    def data(self, key):
        """Expose Open Metadata propeties to model"""
        value = super(Item, self).data(key)

        if not value:
            if key == 'path':
                node = self.data('node')
                value = node.path.as_str

            if key == 'suffix':
                node = self.data('node')
                value = node.path.suffix

            if key == 'display':
                node = self.data('node')
                value = node.path.name

            if key == 'value':
                node = self.data('node')
                value = node.value

        return value

    def set_data(self, key, value):
        if key == 'path':
            node = self.data('node')
            node._path.set(value)
        else:
            return super(Item, self).set_data(key, value)


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
                                 'node': node})
        self.root_item = root
        self.model_reset.emit()

    def flush(self):
        while self.save_queue:
            index = self.save_queue.pop()
            node = self.data(index, 'node')
            node.value = self.data(index, 'value')

            try:
                pifou.om.flush(node)
            except Exception as e:
                # Put index back, so we may try again later.
                self.save_queue.add(index)
                return self.error.emit(e)

        self.flushed.emit()

    def create_item(self, data, parent=None):
        item = Item(data, parent)
        self.register_item(item)
        return item

    def add_entry(self, name, parent, group=False):
        model_parent = self.item(parent)
        entry_parent = self.data(parent, 'node')

        if not group and not '.' in name:
            name += '.string'  # Default to string

        entry = pifou.om.Entry(name, parent=entry_parent)

        if group:
            entry.isparent = True

        # Physically write to disk
        try:
            pifou.om.flush(entry)
        except Exception as e:
            return self.error.emit(e)

        self.add_item({'type': 'om',
                       'node': entry},
                      parent=model_parent)

    def remove_item(self, index):
        # Physically remove `index`
        node = self.data(index, 'node')

        try:
            pifou.om.remove(node)
        except Exception as e:
            return self.error.emit(e)

        super(Model, self).remove_item(index)

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
                                  'node': child},
                                 parent=model_parent)
        else:
            self.create_item({'type': 'om-editor',
                              'node': node,
                              'default': node.value},
                             parent=model_parent)

        super(Model, self).pull(index)

    def set_data(self, index, key, value):
        if key == pigui.pyqt5.model.Value:
            """Save `value` in `index`"""
            self.save_queue.add(index)

        if key == pigui.pyqt5.model.Display:
            """Rename `index` to `value`"""
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

            # Update node with new name
            self.set_data(index, key='path', value=basename)

        super(Model, self).set_data(index, key, value)
