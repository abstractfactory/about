from __future__ import absolute_import

# standard library
import os

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
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# local library
import about
import about.view
import about.item
import about.event
import about.model
import about.settings

pigui.style.register('about')
pigui.setup_log()

about.view.monkey_path()


class About(pigui.pyqt5.widgets.application.widget.ApplicationBase):
    """About controller"""

    flush = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        super(About, self).__init__(parent)

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

    def set_model(self, model):
        self.view.set_model(model)
        self.model = model

        model.saved.connect(self.model_saved_event)
        model.error.connect(self.model_error_event)

        # Delay actions performed on model until a pre-defined timeout.
        # This is so that data won't get written too frequently by quick
        # user interaction.
        self.flush_timer.timeout.connect(model.flush)

    def model_saved_event(self):
        self.notify('Changes saved..')

    def model_error_event(self, exception):
        self.notify(str(exception))

    def event(self, event):
        if event.type() == pigui.pyqt5.event.Type.AddItemEvent:
            """A new item is being created.

            The event comes with the index of the parent in which
            the new item is to be created. We'll use this index to
            find the corresponding List-view and find the "New" item
            within, and place the editor on-top of it.

            """

            lis = self.view.find_list(event.index)
            placeholder = lis.findChild(QtWidgets.QWidget, 'New')
            editor = pigui.pyqt5.widgets.item.CreatorItem('untitled',
                                                          index=event.index,
                                                          parent=placeholder)

            # Overlap placeholder
            editor.resize(placeholder.size())
            editor.show()

        elif event.type() == pigui.pyqt5.event.Type.EditItemEvent:
            """An existing item is being edited.

            Let's place an editor on-top of it.

            """

            label = self.model.data(index=event.index, key='display')
            edited = event.view.indexes[event.index]
            editor = pigui.pyqt5.widgets.item.RenamerItem(label,
                                                          index=event.index,
                                                          parent=edited)
            # Overlap edited
            editor.resize(edited.size())
            editor.show()

        elif event.type() == pigui.pyqt5.event.Type.ItemRenamedEvent:
            """An item has been renamed

            Signal the change to the model.

            """

            item = self.model.item(event.index)
            data = event.data
            self.model.set_data(index=event.index,
                                key=pigui.pyqt5.model.Name,
                                value=data)

            self.flush_timer.start(about.settings.FLUSH_DELAY)

        elif event.type() == pigui.pyqt5.event.Type.ItemCreatedEvent:
            """An item has been created

            Signal the change to the model.

            Behaviour:
                Enter produces a leaf
                Shift-enter produces a group

            """

            # Use `queryKeyboardModifiers()` as opposed to
            # `queryKeyboardModifiers()` due to the latter not
            # always being reliable and causing unpredictable
            # results from the perspective of the user adding
            # a new item.
            group = False
            modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
            if modifiers & QtCore.Qt.ShiftModifier:
                group = True

            name = event.data

            parent_item = self.model.item(event.index)

            try:
                self.model.add_entry(name,
                                     parent=event.index,
                                     group=group)

            except pifou.error.Exists as e:
                self.notify(str(e))

                # Re-open the editor to add more items
                event = pigui.pyqt5.event.AddItemEvent(index=event.index)
                QtWidgets.QApplication.postEvent(self, event)

            # Re-open the editor to add more items
            event = pigui.pyqt5.event.AddItemEvent(index=event.index)
            QtWidgets.QApplication.postEvent(self, event)

        elif event.type() == pigui.pyqt5.event.Type.DataEditedEvent:
            """The data of an item has been modified.

            Signal the change, and count-down until physically writing
            to disk.

            """

            self.model.set_data(index=event.index,
                                key=pigui.pyqt5.model.Value,
                                value=event.data)

            # Start the count-down
            self.flush_timer.start(about.settings.FLUSH_DELAY)

        elif event.type() == pigui.pyqt5.event.Type.RemoveItemEvent:
            """An item has been removed.

            Notify the model.

            """

            item = self.model.item(event.index)
            self.model.remove_item(event.index)

            self.flush_timer.start(about.settings.FLUSH_DELAY)

        elif event.type() == pigui.pyqt5.event.Type.OpenInExplorerEvent:
            item = self.model.item(event.index)
            pigui.service.open_in_explorer(item.path)

        return super(About, self).event(event)


if __name__ == '__main__':
    import pigui.pyqt5.util

    path = os.path.expanduser(r'~')

    with pigui.pyqt5.util.application_context():

        model = about.model.Model()

        win = About()
        win.set_model(model)
        win.resize(*about.settings.WINDOW_SIZE)
        win.show()

        model.setup(uri=r'om:{}'.format(path))
