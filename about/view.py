
import os

import pigui.pyqt5.widgets.list.view
import pigui.pyqt5.widgets.miller.view

import about.delegate
import about.editor

# from PyQt5 import QtWidgets

AbstractList = pigui.pyqt5.widgets.list.view.AbstractList


class List(AbstractList):
    def create_delegate(self, label, index, parent=None):
        delegate = super(List, self).create_delegate(label, index, parent)
        if delegate:
            return delegate

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

        delegate = about.delegate.EntryDelegate(label=label, index=index)

        if ext:
            # For use in CSS
            delegate.setProperty('type', ext.strip("."))

        return delegate


def create_list(self, index):
    lis = List(index)
    return lis


def monkey_path():
    pigui.pyqt5.widgets.miller.view.DefaultMiller.create_list = create_list
