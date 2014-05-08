
import pifou.lib
# import pifou.signal

import pigui.widgets.pyqt5.miller.view


class Miller(pigui.widgets.pyqt5.miller.view.DefaultMiller):
    def column_added_event(self, column):
        super(Miller, self).column_added_event(column)

        item = column.item

        if item.node.iscollection:
            column.placeholders['new'].show()
