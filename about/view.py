
import pigui.pyqt5.widgets.list.view
import pigui.pyqt5.widgets.miller.view

import about.editor
import about.delegate

DefaultList = pigui.pyqt5.widgets.list.view.DefaultList


def create_delegate(self, index):
    typ = self.model.data(index, 'type')

    if typ == 'editor':
        suffix = self.model.data(index, 'suffix')
        default = self.model.data(index, 'default')
        value = self.model.data(index, 'value')

        Editor = about.editor.get(suffix)
        if Editor:
            return Editor(default=value or default, index=index)
        else:
            return about.editor.noeditor.Editor(suffix=suffix, index=index)

    elif typ == 'entry':
        label = self.model.data(index, 'display')
        suffix = self.model.data(index, 'suffix')
        delegate = about.delegate.EntryDelegate(label=label, index=index)
        delegate.setProperty('suffix', suffix)
        return delegate

    else:
        return super(DefaultList, self).create_delegate(index)


def monkey_patch():
    DefaultList.create_delegate = create_delegate
