
import pigui.pyqt5.widgets.list.view
import pigui.pyqt5.widgets.miller.view

import about.editor
import about.delegate

# from PyQt5 import QtWidgets

AbstractList = pigui.pyqt5.widgets.list.view.AbstractList


class List(AbstractList):
    def create_delegate(self, index):
        typ = self.model.data(index, 'type')

        if typ == 'om-editor':
            suffix = self.model.data(index, 'suffix')
            default = self.model.data(index, 'default')
            value = self.model.data(index, 'value')

            Editor = about.editor.get(suffix)
            if Editor:
                return Editor(default=value or default, index=index)
            else:
                return about.editor.noeditor.Editor(suffix=suffix, index=index)

        elif typ == 'om':
            label = self.model.data(index, 'display')
            suffix = self.model.data(index, 'suffix')
            delegate = about.delegate.EntryDelegate(label=label, index=index)
            delegate.setProperty('type', suffix)
            return delegate

        else:
            return super(List, self).create_delegate(index)


def create_list(self, index):
    lis = List(index)
    return lis


def monkey_path():
    pigui.pyqt5.widgets.miller.view.DefaultMiller.create_list = create_list
