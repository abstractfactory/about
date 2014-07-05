# standard library
import os

# pifou library
import pifou.metadata
import pifou.lib

# pigui library
import pigui.pyqt5.model

# pigui dependency
from PyQt5 import QtCore


class Item(pigui.pyqt5.model.ModelItem):
    """Custom model item for About

    Changes:
        As opposed to storing plain paths as per the default model
        implementation, the About model stores the Open Metadata objects
        within each item. The :meth:`.data` method then accesses this
        object along with providing the expected behaviour.

        data:
            path (str): Retrieve the full path from OM object
            suffix (str): Retrieve suffix from OM object
            display (str): Name of OM object
            value (object): Value from OM object, this may be
                of varying types and depends on the contained OM object.
            isgroup (bool): Adapter for openmetadata.Entry.isparent

    """

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
        """Override :meth:`.set_data` from default implementation"""
        if key == 'path':
            node = self.data('node')
            node._path.set(value)
        else:
            return super(Item, self).set_data(key, value)


@pifou.lib.log
class Model(pigui.pyqt5.model.Model):
    """Custom model for About

    This implements delayed writing to disk via `flushing`. To
    flush means to physically write to disk.

    Attributes:
        flushed: Signal, emitted whenever the model flushes changes
            to disk.
        save_queue: Delayed writes are stored here.

    """

    flushed = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.save_queue = set()

    def setup(self, location):
        """Populate model with absolute path `location`

        Arguments:
            location (str): Absolute path to root directory from
                which to pull metadata.

        """

        node = pifou.metadata.Location(location)
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
                pifou.metadata.flush(node)
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

        entry = pifou.metadata.Entry(name, parent=entry_parent)

        if group:
            entry.isparent = True

        # Physically write to disk
        try:
            pifou.metadata.flush(entry)
        except Exception as e:
            return self.error.emit(e)

        self.add_item({'type': 'entry',
                       'node': entry},
                      parent=parent)

    def remove_item(self, index):
        # Physically remove `index`
        node = self.data(index, 'node')

        try:
            pifou.metadata.remove(node)
        except Exception as e:
            return self.error.emit(e)

        super(Model, self).remove_item(index)

    def pull(self, index):
        node = self.data(index, 'node')

        try:
            pifou.metadata.pull(node)
        except pifou.metadata.error.Exists:
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
