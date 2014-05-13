
import openmetadata as om

# pifou library
import pifou
import pifou.om
import pifou.lib
import pifou.signal

# pigui library
import pigui
import pigui.style
import pigui.widgets.pyqt5.application

# pigui dependencies
from PyQt5 import QtGui
from PyQt5 import QtCore
from PyQt5 import QtWidgets

# Local library
import about.item
import about.view
import about.editor

about.view.register()
pigui.style.register('about')

om.setup_log()
pifou.setup_log()
pigui.setup_log()


class Widget(pigui.widgets.pyqt5.application.ApplicationBase):
    """About graphical user interface"""
    WINDOW_SIZE = (600, 200)  # px
    FLUSH_DELAY = 2000  # ms

    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)

        self.item = None
        self.miller = None

        # Signals
        self.flushed = pifou.signal.Request(quiet=bool)
        self.removed = pifou.signal.Request(node=object)
        self.modified = pifou.signal.Signal(node=object, value=object)
        self.added = pifou.signal.Request(name=basestring,
                                          parent=object,
                                          isparent=bool)

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
            print "event_handler(): modifying %s=%s" % (item, value)
            self.modified_event(item, value)

    def flush(self, quiet=False, confirm=False):
        """Process all pending tasks

        Parameters
            quiet   -- Do not notify user

        """

        self.flush_timer.stop()

        # Emit request
        success = self.flushed(quiet)

        if success == 'nothing-to-save':
            self.notify('Information', 'Nothing to save..')
            return True

        if confirm and not success:
            return self.confirm(
                "Couldn't flush",
                "There were pending writing operations, but they "
                "failed. If you close, they will be lost into "
                "oblivion. \n\nClose?")

        if not quiet:
            self.notify('Saved', 'Changes saved')

        return True

    def toggle_cascading(self, inherit=False):
        # method = om.inherit if inherit else om.pull
        # about.item.pull_method = method
        # self.reload()
        self.notify('Cascading', 'Cascading metadata %s' %
                    ('ON' if inherit else 'OFF'))

    def remove_selected(self):
        """Remove currently selected item from datastore"""
        current_item = self.miller.selection_model.current
        self.remove(current_item)

    def remove(self, item):
        """Remove `item` from datastore"""
        self.removed.emit(item.node)

        metalist = item.view
        metalist.remove_item(item)

    def modified_event(self, item, value):
        """A node has been modified via an editor"""
        if value:
            self.modified.emit(node=item.node, value=value)

        self.flush_timer.start(self.FLUSH_DELAY)

    def item_added_event(self, name, item, widget):
        # Use `queryKeyboardModifiers()` as opposed to queryKeyboardModifiers()
        # due to the latter not always being reliable and causing unpredictable
        # results from the perspective of the user adding a new item.
        isparent = False
        modifiers = QtWidgets.QApplication.queryKeyboardModifiers()
        if modifiers & QtCore.Qt.ShiftModifier:
            isparent = True

        # Request a new node to be added
        new_node, status = self.added(name, item.node, isparent)

        # Does it already exist?
        if status == 'exists':
            return self.notify('Exists', '%s already exists' % name)

        # Is it about to be written?
        if status == 'queued':
            return self.notify('Patience', '%s is about '
                               'to be written' % name)

        new_item = about.item.EntryItem.from_node(new_node)
        # self.modified_event(new_item, None)

        widget.add_item(new_item)
        # widget.sort()

        # self.flush()

        if status == 'success':
            return self.notify('Message', '%s added' % name)

    def loaded_event(self, item):
        self.item = item
        self.miller.clear()
        self.miller.load(item)

    def reload(self):
        # old_location = self.item.node
        # new_location = om.Location(old_location.raw_path)
        # item = self.item.from_node(new_location)
        self.loaded_event(item)

    def animated_close(self):
        if self.safe_to_close:
            return super(Widget, self).animated_close()

        if self.flush(confirm=True, quiet=True):
            self.safe_to_close = True
            return super(Widget, self).animated_close()

    def closeEvent(self, event):
        if self.safe_to_close:
            return super(Widget, self).closeEvent(event)

        if not self.flush(confirm=True, quiet=True):
            return event.ignore()

        super(Widget, self).closeEvent(event)


class Application(object):
    """About business-logic"""

    DEFAULT_TYPE = 'string'

    def __init__(self, widget=None):
        self.widget = widget or Widget
        self.loaded = pifou.signal.Signal()

        self.save_queue = set()
        self.remove_queue = set()

    def init_widget(self):
        widget = self.widget()

        self.loaded.connect(widget.loaded_event)

        widget.flushed.connect(self.flush)
        widget.removed.connect(self.remove)
        widget.modified.connect(self.modify)
        widget.added.connect(self.add)

        widget.animated_show()

        self.widget = widget

    def load(self, location):
        # item = about.item.LocationItem.from_node(location)
        item = about.item.LocationItem.from_node(location)
        # print "Loading %s" % item
        self.loaded.emit(item)

    def add(self, name, parent, isparent):
        path = parent.path + name
        if not path.suffix:
            path = path.copy(suffix=self.DEFAULT_TYPE)

        new_node = pifou.pom.node.Node.from_str(path.as_str)
        new_node.isparent = isparent
        # print "Adding %s to %s" % (name, parent)
        return new_node, 'success'

    def flush(self, quiet=False):
        status = 'nothing-to-save'

        if not self.save_queue and not self.remove_queue:
            return status

        while self.save_queue:
            node = self.save_queue.pop()

            # parent = pifou.om.convert(node.path.parent.as_str)
            # assert parent
            # print "node.path=%s" % node.path
            # print "parent=%s" % parent.path
            # entry = pifou.om.Entry(node.path.name, parent=parent)
            # entry.value = node.data['value']
            # print "saving %s=%s" % (entry.path, entry.value)

            status = 'saved'
            # om.flush(entry)

        while self.remove_queue:
            node = self.remove_queue.pop()

            entry = pifou.om.convert(node.path.as_str)
            om.remove(entry)

            status = 'saved'

        return status

    def remove(self, node):
        if node in self.save_queue:
            self.save_queue.remove(node)
        else:
            self.remove_queue.add(node)
            self.flush_timer.start(self.FLUSH_DELAY)

    def modify(self, node, value):
        # print "Modifying %s=%s" % (node, value)
        node.data['value'] = value
        self.save_queue.add(node)


def main(path):
    import pigui.util.pyqt5

    node = pifou.pom.node.Node.from_str(path)
    app = Application()

    # with pigui.util.pyqt5.app_context(use_baked_css=True):
    with pigui.util.pyqt5.app_context():
        app.init_widget()
        app.load(node)


if __name__ == '__main__':
    main(r'c:\users\marcus\om')
    # main(r'C:\Users\marcus\Dropbox\Apps')
    # main(r'S:\content\jobs\machine')
