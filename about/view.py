
import os

import pigui.pyqt5.widgets.list.view
import pigui.pyqt5.widgets.miller.view

import about.item
import about.editor

# from PyQt5 import QtWidgets

AbstractList = pigui.pyqt5.widgets.list.view.AbstractList


class List(AbstractList):
    def create_item(self, label, index, parent=None):
        item = super(List, self).create_item(label, index, parent)
        if item:
            return item

        uri = self.model.uri(index)
        path = self.model.path(uri)
        args, kwargs = self.model.options(uri)
        _, ext = os.path.splitext(path)

        if 'editor' in args:
            Editor = about.editor.get(ext)

            if Editor:
                value = self.model.data(index, key='value')
                default = self.model.data(index, key='default')
                return Editor(default=value or default, index=index)

            else:
                Editor = about.editor.get('no-editor')
                return Editor(ext, index=index)

        item = about.item.EntryItem(label=label, index=index)

        if ext:
            # For use in CSS
            item.setProperty('type', ext.strip("."))

        return item


def create_list(self, index):
    lis = List(index)
    return lis


def monkey_path():
    pigui.pyqt5.widgets.miller.view.DefaultMiller.create_list = create_list
