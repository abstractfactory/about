
import openmetadata as om
om.setup_log()

# pifou library
import pifou
import pifou.om
import pifou.lib
import pifou.signal

# For flags
import about


@pifou.lib.log
class About(object):
    """About business-logic

    Description
        This is the business logic of About which handles all non-gui
        functionality. `application.About` communicates with `widget.About`
        via `pifou.signal`, this is their only means of communication.

    Push/pull | Node.data['value']
        Data is being retrieved using `pifou.om`and intermediately
        stored within `pifou.pom.node` until written.

        See `About.modified` for implementation details

    """

    DEFAULT_TYPE = 'string'

    def __init__(self):
        self.widget = None
        self.loaded = pifou.signal.Signal()

        self.save_queue = set()
        self.remove_queue = set()

    def init_widget(self, widget):
        self.loaded.connect(widget.loaded_event)

        # Signals
        widget.removed.connect(self.remove)
        widget.modified.connect(self.modify)

        # Requests
        widget.request_flush.connect(self.flush)
        widget.request_add.connect(self.add)

        widget.animated_show()

        self.widget = widget

    def load(self, node):
        """Load `node`

        Description
            Incoming node has the following path:
            $ /home/marcus

            But needs to reflect the metadata container-path:
            $ /home/marcus/.meta

        """

        # Convert node to Open Metadata path
        path = node.path
        if not path.as_str.endswith(pifou.om.Path.CONTAINER):
            path += pifou.om.Path.CONTAINER
            node = node.copy(path=path)

        self.loaded.emit(node)

    def add(self, name, parent, isparent):
        """Add `name` to `parent`

         ____
        |____|______
        |          |\
        |   __|__    |
        |     |      |
        |____________|

        """

        print "Looking for %s in %s" % (name, parent.path)
        exists = pifou.om.find(parent.path.as_str, name)
        if exists:
            return exists, about.EXISTS

        path = parent.path + name
        if not isparent and not path.suffix:
            path = path.copy(suffix=self.DEFAULT_TYPE)

        new_node = pifou.pom.node.Node.from_str(path.as_str)
        new_node.isparent = isparent

        # Set default value
        value = pifou.om.default(path.suffix)
        new_node.data['value'] = value

        self.save_queue.add(new_node)

        return new_node, about.SUCCESS

    def remove(self, node):
        """Remove `node` from datastore

         ____
        |____|______
        |          |\
        |    ___     |
        |            |
        |____________|


        """

        if node in self.save_queue:
            self.save_queue.remove(node)
        else:
            self.remove_queue.add(node)

    def modify(self, node, value):
        """Inject `value` into `node`

         ____
        |____|______
        |          |\
        |            |
        |     ?      |
        |____________|


        """

        node.data['value'] = value
        self.save_queue.add(node)

    def flush(self):
        """Commit changes to datastore

         ____
        |____|______
        |     __   |\
        |    _||_    |
        |    \  /    |
        |_____\/_____|

        """

        status = about.NOTHING_TO_SAVE

        if not self.save_queue and not self.remove_queue:
            return status

        while self.save_queue:
            node = self.save_queue.pop()

            entry = pifou.om.convert(node.path.as_str)
            entry.isparent = node.isparent

            if not entry.isparent:
                entry.value = node.data['value']

            pifou.om.flush(entry)

            status = about.SAVED

        while self.remove_queue:
            node = self.remove_queue.pop()

            entry = pifou.om.convert(node.path.as_str)
            pifou.om.remove(entry)

            status = about.SAVED

        return status
