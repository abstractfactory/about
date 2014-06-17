# standard library
import os
import openmetadata

# pifou library
import pifou.om

# pigui library
import pigui.pyqt5.model

# pigui dependency
from PyQt5 import QtCore


openmetadata.setup_log()


class Item(pigui.pyqt5.model.UriItem):
    def __init__(self, *args, **kwargs):
        super(Item, self).__init__(*args, **kwargs)


class Model(pigui.pyqt5.model.Model):
    error = QtCore.pyqtSignal(Exception)
    saved = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.save_queue = set()

    def create_item(self, location, metapath, parent=None):
        item = Item(location, metapath, parent)
        return item

    def add_entry(self, name, parent, group=False):
        """
        Arguments:
            name -- Name of entry
            parent -- Parent index of entry
            group -- Entry is a parent

        """

        if not '.' in name:
            name += '.string'  # Default to string

        parent = self.indexes[parent]
        entry = pifou.om.Entry(name, parent=parent.entry)
        item = self.create_item(entry, 


    def add_item(self, uri, parent=None):
        """Add `uri` to `parent`"""

        scheme = self.scheme(uri)
        path = self.path(uri)
        args, kwargs = self.options(uri)

        if scheme == 'om':
            """Write Open Metadata"""

            dirname = os.path.dirname(path)
            basename = os.path.basename(path)
            name, _ = os.path.splitext(basename)

            # Does it exist on disk?
            if pifou.om.find(os.path.dirname(path), name):
                e = pifou.error.Exists("%s already exists" % name)
                return self.error.emit(e)

            parent_ = pifou.om.convert(dirname)
            entry = pifou.om.Entry(basename, parent=parent_)
            entry.isparent = kwargs.get('type') == pigui.pyqt5.model.FOLDER

            try:
                pifou.om.flush(entry)
            except Exception as e:
                # Something went wrong, do not
                # add it to the model.
                return self.error.emit(e)

            assert os.path.exists(entry.path.as_str), entry.path.as_str

            self.saved.emit()

        print "Adding %s" % uri
        super(Model, self).add_item(uri, parent)

    def remove_item(self, index):
        item = self.indexes[index]
        path = item.path
        entry = pifou.om.convert(path)
        pifou.om.remove(entry)

        super(Model, self).remove_item(index)

    def flush(self):
        """Perform tasks in queues"""
        while self.save_queue:
            index = self.save_queue.pop()
            item = self.indexes[index]
            path = item.path
            value = item.data('value')

            # Converting
            entry = pifou.om.convert(path)
            entry.value = value
            pifou.om.flush(entry)

        self.saved.emit()

    def set_data(self, index, key, value):
        item = self.indexes[index]
        args, kwargs = item.options

        if 'editor' in args:
            # Data was edited
            self.save_queue.add(index)

        if key == pigui.pyqt5.model.Name:
            # An existing item was renamed
            old_path = item.path
            dirname = os.path.dirname(old_path)

            if pifou.om.find(dirname, value):
                e = pifou.error.Exists("%s already exists" % value)
                return self.error.emit(e)

            old_basename = os.path.basename(old_path)
            old_name, old_suffix = os.path.splitext(old_basename)
            new_path = os.path.join(dirname, value + old_suffix)

            try:
                os.rename(old_path, new_path)
            except OSError as e:
                return self.error.emit(e)

            # Make sure to refresh item after rename
            item.clear()

            # Override key to display new name
            key = 'display'
            self.saved.emit()

        super(Model, self).set_data(index, key, value)

    def pull(self, index):
        """Append editors to files"""

        root = self.indexes[index]
        print "pulling %s" % root.uri
        print "pulling %s" % root.path
        entry = pifou.om.convert(root.path)

        try:
            pifou.om.pull(entry)
        except pifou.om.error.Exists:
            pass

        # Append Header item
        self.create_item(uri='memory:Header', parent=root)

        # Append additional entries
        if entry.isparent:
            print "pulling folder"
            for child in entry:
                uri = "om:" + child.path.as_str
                item = self.create_item(uri=uri, parent=root)
                typ = (pigui.pyqt5.model.FOLDER
                       if entry.isparent
                       else pigui.pyqt5.model.FILE)
                item.set_data(key='type', value=typ)

            # Append New item
            self.create_item(uri='memory:New', parent=root)

        # Append editor
        else:
            print "pulling non-folder"
            uri = root.uri
            if '?' in root.uri:
                uri += "#editor"
            else:
                uri += '?editor'

            child_item = self.create_item(uri=uri, parent=root)
            default = entry.value
            child_item.set_data(key='default', value=default)
