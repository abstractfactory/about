from __future__ import absolute_import

# standard library
import os
import errno
import logging

# pifou library
import pifou.error

# pigui library
import pigui
import pigui.style
import pigui.service
import pigui.pyqt5.event
import pigui.pyqt5.model
import pigui.pyqt5.widgets.miller.view
import pigui.pyqt5.widgets.application.widget

# pigui dependency
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# local library
import about
import about.view
import about.model
import about.settings

pigui.style.register('about')

about.view.monkey_patch()

log = logging.getLogger('about')
log.setLevel(logging.INFO)
# log.setLevel(logging.WARNING)

formatter = logging.Formatter(
    '%(asctime)s - '
    '%(levelname)s - '
    '%(name)s - '
    '%(message)s',
    '%H:%M:%S')

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)
log.addHandler(stream_handler)


class About(pigui.pyqt5.widgets.application.widget.ApplicationBase):
    """About controller"""

    flush = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(About, self).__init__(parent)
        self.setWindowTitle('About')

        # Pad the view, and inset background via CSS
        canvas = QtWidgets.QWidget()
        canvas.setObjectName('Canvas')

        view = pigui.pyqt5.widgets.miller.view.DefaultMiller()
        view.setObjectName('View')
        view.setSizePolicy(QtWidgets.QSizePolicy.MinimumExpanding,
                           QtWidgets.QSizePolicy.MinimumExpanding)

        layout = QtWidgets.QHBoxLayout(canvas)
        layout.setContentsMargins(1, 1, 1, 1)
        layout.addWidget(view)

        widget = QtWidgets.QWidget()

        layout = QtWidgets.QHBoxLayout(widget)
        layout.addWidget(canvas)
        layout.setContentsMargins(5, 0, 5, 5)
        layout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop)

        self.set_widget(widget)

        flush_timer = QtCore.QTimer()
        flush_timer.setSingleShot(True)

        # References
        self.view = view
        self.model = None
        self.flush_timer = flush_timer

        save_sequence = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        save_key = QtWidgets.QShortcut(save_sequence, self)
        save_key.activated.connect(self.flush)

    def flush(self):
        self.flush_timer.stop()
        self.model.flush()

    def set_model(self, model):
        self.view.set_model(model)
        self.model = model

        model.flushed.connect(self.model_flushed_event)
        model.error.connect(self.model_error_event)

        # Delay actions performed on model until a pre-defined timeout.
        # This is so that data won't get written too frequently by quick
        # user interaction.
        self.flush_timer.timeout.connect(model.flush)

    def model_flushed_event(self):
        self.notify('Changes saved..')

    def model_error_event(self, exception):
        if isinstance(exception, OSError):
            if exception.errno == errno.EEXIST:
                self.notify("Already exists")
        else:
            self.notify(str(exception))

    def event(self, event):

        # Events handled
        AddItemEvent = pigui.pyqt5.event.Type.AddItemEvent
        EditItemEvent = pigui.pyqt5.event.Type.EditItemEvent
        ItemRenamedEvent = pigui.pyqt5.event.Type.ItemRenamedEvent
        ItemCreatedEvent = pigui.pyqt5.event.Type.ItemCreatedEvent
        DataEditedEvent = pigui.pyqt5.event.Type.DataEditedEvent
        RemoveItemEvent = pigui.pyqt5.event.Type.RemoveItemEvent
        OpenInExplorerEvent = pigui.pyqt5.event.Type.OpenInExplorerEvent
        Close = QtCore.QEvent.Close

        # Handlers
        if event.type() == Close:
            # Save changes on close
            # TODO: Ignore close on error
            self.flush()

        if event.type() == AddItemEvent:
            """A new item is being created.

            The event comes with the index of the parent in which
            the new item is to be created. We'll use this index to
            find the corresponding List-view and find the "Footer" item
            within, and place the editor on-top of it.

            """

            # Add to parent, not the Footer item
            index = event.index
            if self.model.data(event.index, 'type') == 'Footer':
                index = self.model.data(event.index, 'parent')

            # Do not add anything to leaf-entries
            if not self.model.data(index, 'isgroup'):
                lis = self.view.find_list(index)
                placeholder = lis.findChild(QtWidgets.QWidget, 'Footer')
                editor = pigui.pyqt5.widgets.delegate.CreatorDelegate(
                    'untitled',
                    index=index,
                    parent=placeholder)

                # Overlap placeholder
                editor.resize(placeholder.size())
                editor.show()

        elif event.type() == EditItemEvent:
            """An existing item is being edited.

            Place an editor on-top of it.

            """

            label = self.model.data(index=event.index, key='display')
            edited = event.view.indexes[event.index]
            editor = pigui.pyqt5.widgets.delegate.RenamerDelegate(
                label,
                index=event.index,
                parent=edited)

            # Overlap edited
            editor.resize(edited.size())
            editor.show()

        elif event.type() == ItemRenamedEvent:
            """An item is being renamed

            Signal the change to the model.

            """

            name = event.data
            self.model.set_data(index=event.index,
                                key=pigui.pyqt5.model.Display,
                                value=name)

            self.flush_timer.start(about.settings.FLUSH_DELAY)

        elif event.type() == ItemCreatedEvent:
            """An item is being created

            Signal the change to the model.

            Behaviour:
                - Enter produces a leaf
                - Shift-enter produces a group

            """

            group = False
            modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
            if modifiers & QtCore.Qt.ShiftModifier:
                group = True

            label = event.data
            parent = event.index

            try:
                self.model.add_entry(name=label,
                                     group=group,
                                     parent=parent)

            except pifou.error.Exists as e:
                self.notify(str(e))

            # Re-open the editor to add more items
            event = pigui.pyqt5.event.AddItemEvent(index=event.index)
            QtWidgets.QApplication.postEvent(self, event)

        elif event.type() == DataEditedEvent:
            """The data of an item is being modified.

            Signal the change, and count-down until physically writing
            to disk.

            """

            self.model.set_data(index=event.index,
                                key=pigui.pyqt5.model.Value,
                                value=event.data)

            # Start the count-down
            self.flush_timer.start(about.settings.FLUSH_DELAY)

        elif event.type() == RemoveItemEvent:
            """An item is being removed.

            Notify the model.

            """

            self.model.remove_item(event.index)

        elif event.type() == OpenInExplorerEvent:
            path = self.model.data(event.index, 'path')
            pigui.service.open_in_explorer(path)

        return super(About, self).event(event)


if __name__ == '__main__':
    import pigui
    import pifou
    import logging
    import openmetadata

    log = pigui.setup_log()
    log.setLevel(logging.DEBUG)

    log = pifou.setup_log()
    log.setLevel(logging.DEBUG)

    log = openmetadata.setup_log()
    log.setLevel(logging.DEBUG)

    import pigui.pyqt5.util

    path = os.path.expanduser(r'~')

    with pigui.pyqt5.util.application_context():

        model = about.model.Model()

        win = About()
        win.set_model(model)
        win.resize(*about.settings.WINDOW_SIZE)
        win.show()

        model.setup(path)
