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

        if not value and self.data('type') in ('entry', 'editor'):
            if key == 'path':
                node = self.data('node')
                value = node.path.as_str

            elif key == 'suffix':
                node = self.data('node')
                value = node.path.suffix

            elif key == 'display':
                node = self.data('node')
                value = node.name

            elif key == 'value':
                node = self.data('node')
                value = node.value

            elif key == 'isgroup':
                value = self.data('node').isparent

        return value

    def set_data(self, key, value):
        if key == 'path':
            node = self.data('node')
            node._path.set(value)
        else:
            return super(Item, self).set_data(key, value)


@pifou.lib.log
class Model(pigui.pyqt5.model.Model):
    flushed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.save_queue = set()

    def setup(self, location):
        node = pifou.om.Location(location)
        root = self.create_item({'type': 'entry',
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
                self.error.emit(e)
                raise

        self.flushed.emit()

    def create_item(self, data, parent=None):
        item = Item(data, parent=self.indexes.get(parent))
        self.register_item(item)
        return item

    def add_entry(self, name, parent, group=False):
        """Add new Open Metadarta Entry onto self

        Arguments:
            name (str): Name of new Entry
            parent (str): Index of new Model Item
            group (bool): Should the entry be able to contain children?

        """

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

        self.add_item({'type': 'entry',
                       'node': entry},
                      parent=parent)

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

        if node.isparent:
            for child in node:
                self.create_item({'type': 'entry',
                                  'node': child},
                                 parent=index)
        else:
            print "Adding editor to: %s" % node.path
            self.create_item({'type': 'editor',
                              'node': node,
                              'default': node.value},
                             parent=index)

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
            else:
                old = os.path.basename(old_path)
                new = os.path.basename(new_path)
                self.status.emit("Renamed {} to {}".format(old, new))

            # Update node with new name
            self.set_data(index, key='path', value=basename)

        super(Model, self).set_data(index, key, value)
