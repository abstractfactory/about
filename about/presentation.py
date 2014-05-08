
import openmetadata as om
om.setup_log('openmetadata')

# pifou library
import pifou
import pifou.lib
import pifou.signal
pifou.setup_log()

# pigui library
import pigui
import pigui.style
import pigui.widgets.pyqt5.application
pigui.setup_log()

# pigui dependencies
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# Local library
import about.view
import about.editor
import about.entryitem

# Register supported editors
about.editor.register()


# Register style
pigui.style.register('about')


class Widget(pigui.widgets.pyqt5.application.ApplicationBase):
    WINDOW_SIZE = (700, 500)  # px
    FLUSH_DELAY = 4000  # ms

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        self.item = None
        self.miller = None

        self.save_queue = set()
        self.remove_queue = set()
        self.flush_timer = QtCore.QTimer()
        self.flush_timer.timeout.connect(self.flush)
        self.safe_to_close = False

        def setup_header():
            cascading = QtWidgets.QPushButton()
            cascading.setCheckable(True)
            cascading.setObjectName('CascadingButton')
            cascading.toggled.connect(self.toggle_cascading)
            cascading.setToolTip('Cascading metadata')

            header = super(Widget, self).findChild(QtWidgets.QWidget, 'Header')
            layout = header.layout()
            layout.insertWidget(0, cascading)

            return header

        def setup_body():
            body = QtWidgets.QWidget()

            miller = about.view.Miller()
            miller.setObjectName('Body')

            # Signals
            miller.new_item_added.connect(self.item_added_event)
            miller.event.connect(self.event_handler)

            layout = QtWidgets.QHBoxLayout(body)
            layout.addWidget(miller)
            layout.setContentsMargins(0, 0, 0, 0)

            self.miller = miller

            return body

        setup_header()
        body = setup_body()

        superclass = super(Widget, self)
        container = superclass.findChild(QtWidgets.QWidget, 'Container')
        layout = container.layout()
        layout.addWidget(body)
        layout.setContentsMargins(5, 0, 5, 5)

        self.item_added = pifou.signal.Signal(data=object)

        # Overlay saved
        self.saved_widget = QtWidgets.QLabel('saved', self)
        self.saved_widget.hide()

        # Hotkey
        save_sequence = QtGui.QKeySequence(QtCore.Qt.CTRL + QtCore.Qt.Key_S)
        save_key = QtWidgets.QShortcut(save_sequence, self)
        save_key.activated.connect(self.flush)

        remove_sequence = QtGui.QKeySequence(QtCore.Qt.Key_Delete)
        remove_key = QtWidgets.QShortcut(remove_sequence, self)
        remove_key.activated.connect(self.remove_selected)

        self.resize(*self.WINDOW_SIZE)

    def event_handler(self, name, data):
        if name == 'modified':
            value, item = data[:2]
            self.modified_event(value, item)

    def flush(self, quiet=False, confirm=False):
        """Process all pending tasks

        Parameters
            quiet   -- Do not notify user

        """

        def flush(quiet=False):
            self.flush_timer.stop()

            if not self.save_queue and not self.remove_queue:
                return True

            while self.save_queue:
                node = self.save_queue.pop()
                om.flush(node)

            while self.remove_queue:
                node = self.remove_queue.pop()
                om.remove(node)

            if not quiet:
                self.notify('Saved', 'Changes saved')

            return True

        success = flush(quiet)
        if confirm and not success:
            return self.confirm(
                "Couldn't flush",
                "There were pending writing operations, but they "
                "failed. If you close, they will be lost into "
                "oblivion. \n\nClose?")

        return success

    def toggle_cascading(self, inherit=False):
        method = om.inherit if inherit else om.pull
        about.entryitem.pull_method = method
        self.reload()
        self.notify('Cascading', 'Cascading metadata %s' %
                    ('ON' if inherit else 'OFF'))

    def remove_selected(self):
        """Remove currently selected item from database"""
        current_item = self.miller.selection_model.current
        self.remove(current_item)

    def remove(self, item):
        """Remove `item` from database"""
        node = item.node

        if node in self.save_queue:
            self.save_queue.remove(node)
        else:
            self.remove_queue.add(node)
            self.flush_timer.start(self.FLUSH_DELAY)

        metalist = item.view
        metalist.remove_item(item)

    def modified_event(self, value, item):
        """A node has been modified via an editor"""
        node = item.node

        if value is not None:
            # When there is a value included
            # in the event, update node. This won't be
            # the case when e.g. when calling this event manually.
            node.value = value

        self.save_queue.add(node)
        self.flush_timer.start(self.FLUSH_DELAY)

    def item_added_event(self, name, item, widget, iscollection=False):
        new_node = om.Entry(name, parent=item.node)

        # Use `queryKeyboardModifiers()` as opposed to queryKeyboardModifiers()
        # due to the latter not always being reliable and causing unpredictable
        # results from the perspective of the user adding a new item.
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        if modifiers & QtCore.Qt.ShiftModifier:
            iscollection = True

        new_node.iscollection = iscollection

        # Does it already exist?
        parent_path = item.node.path.as_str
        if om.find(parent_path, name):
            return self.notify('Exists', '%s already exists' % name)

        # Is it about to be written?
        if new_node in self.save_queue:
            return self.notify('Patience', '%s is about '
                               'to be written' % name)

        # If user doesn't specify a suffix,
        # default to being of type string.
        if not new_node.iscollection and not new_node.path.suffix:
            new_node.value = ''

        new_item = about.entryitem.EntryItem.from_node(new_node)
        self.modified_event(None, new_item)

        widget.add_item(new_item)
        widget.sort()

        self.flush()

    def load(self, item):
        self.item = item
        self.miller.clear()
        self.miller.load(item)
        print "loading %r" % item

    def reload(self):
        old_location = self.item.node
        new_location = om.Location(old_location.raw_path)
        item = self.item.from_node(new_location)
        self.load(item)

    def animated_close(self):
        if self.safe_to_close:
            return super(Widget, self).animated_close()

        if self.flush(confirm=True):
            self.safe_to_close = True
            return super(Widget, self).animated_close()

    def closeEvent(self, event):
        if self.safe_to_close:
            return super(Widget, self).closeEvent(event)

        if not self.flush(confirm=True):
            return event.ignore()

        super(Widget, self).closeEvent(event)


class Application(object):
    def __init__(self, widget=None):
        self.widget = widget or Widget()

    def load(self, location):
        item = about.entryitem.LocationItem.from_node(location)
        self.widget.load(item)


def main(path):
    import pigui.util.pyqt5

    location = om.Location(path)

    with pigui.util.pyqt5.app_context(use_baked_css=True):
        app = Application()
        app.load(location)
        app.widget.animated_show()


if __name__ == '__main__':
    # main(r'c:\users\marcus')
    # main(r'C:\Users\marcus\Dropbox\Apps')
    main(r'S:\content\jobs\machine')
