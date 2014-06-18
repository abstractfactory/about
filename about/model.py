# standard library
import os

# pifou library
import pifou.om

# pigui library
import pigui.pyqt5.model

# pigui dependency
import openmetadata
from PyQt5 import QtCore

# local library
import about.key

# Dev-temp
openmetadata.setup_log()


# class Item(pigui.pyqt5.model.ModelItem):
#     def __init__(self, node, *args, **kwargs):
#         super(Item, self).__init__(*args, **kwargs)
#         self.node = node


class Model(pigui.pyqt5.model.Model):
    error = QtCore.pyqtSignal(Exception)
    saved = QtCore.pyqtSignal()

    def __init__(self, *args, **kwargs):
        super(Model, self).__init__(*args, **kwargs)
        self.save_queue = set()

    def create_node(self, node, parent=None):
        """Wrap `node` in data, and return item"""
        data = {'node': node,
                'type': 'om'}

        return self.create_item(data)

    def add_item(self, name, parent, group=False):
        """
        Arguments:
            name -- Name of node
            parent -- Parent index of node
            group -- Entry is a parent

        """

        if not '.' in name:
            name += '.string'  # Default to string

        parent = self.indexes[parent]
        node = pifou.om.Entry(name, parent=parent.node)

        if group:
            node.isparent = True
        else:
            node.isparent = False

        self.create_node(node=node, parent=parent)

    def setup(self, location):
        location = pifou.om.Location(location)
        root_item = self.create_node(node=location, parent=None)

        self.root_item = root_item
        self.model_reset.emit()

    def remove_item(self, index):
        # item = self.indexes[index]
        # node = item.data('node')
        # pifou.om.remove(node)

        super(Model, self).remove_item(index)

    def flush(self):
        """Perform tasks in queues"""
        while self.save_queue:
            index = self.save_queue.pop()
            # item = self.indexes[index]
            # node = item.data('node')
            # value = item.data('value')

            # # Inject and write
            # node.value = value
            # pifou.om.flush(node)

        self.saved.emit()

    def data(self, index, key):
        if key == 'path':
            item = self.indexes[index]
            return item.data('path')
        return super(Model, self).data(index, key)

    def set_data(self, index, key, value):
        item = self.indexes[index]
        args, kwargs = item.options

        # if 'editor' in args:
        #     # Data was edited
        #     self.save_queue.add(index)

        # if key == pigui.pyqt5.model.Name:
        #     # An existing item was renamed
        #     old_path = item.path
        #     dirname = os.path.dirname(old_path)

        #     if pifou.om.find(dirname, value):
        #         e = pifou.error.Exists("%s already exists" % value)
        #         return self.error.emit(e)

        #     old_basename = os.path.basename(old_path)
        #     old_name, old_suffix = os.path.splitext(old_basename)
        #     new_path = os.path.join(dirname, value + old_suffix)

        #     try:
        #         os.rename(old_path, new_path)
        #     except OSError as e:
        #         return self.error.emit(e)

        #     # Make sure to refresh item after rename
        #     item.clear()

        #     # Override key to display new name
        #     key = 'display'
        #     self.saved.emit()

        super(Model, self).set_data(index, key, value)

    # def pull(self, index):
    #     """Append editors to files"""

    #     root = self.indexes[index]
    #     entry = root.entry

    #     try:
    #         pifou.om.pull(entry)
    #     except pifou.om.error.Exists:
    #         pass

    #     # Append additional entries
    #     if entry.isparent:
    #         for child in entry:
    #             self.create_item(node=child, parent=root)

    #     # # Append editor
    #     # else:
    #     #     child_item = self.create_item(uri=uri, parent=root)
    #     #     default = entry.value
    #     #     child_item.set_data(key='default', value=default)
