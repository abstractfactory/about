
# import os
import pifou.lib

import pigui.widgets.pyqt5.list.view
import pigui.widgets.pyqt5.miller.view

import about.editor
import about.source


class Miller(pigui.widgets.pyqt5.miller.view.DefaultMiller):

    source = about.source

    def pull(self, item):
        if item.node.isparent:
            self.source.pull(item.node, lazy=True)
        return item

    def column_added_event(self, column):
        super(Miller, self).column_added_event(column)

        item = column.item

        if item.node.isparent:
            column.placeholders['new'].show()


class List(pigui.widgets.pyqt5.list.view.DefaultList):

    predicate = Miller

    def load(self, item):
        super(List, self).load(item)

        # Append editors
        node = item.node
        suffix = node.path.suffix

        family = about.editor.get(suffix) if suffix else None

        if family:
            widget = family.WidgetClass()
            item = family.ItemClass(node, widget)
            self.add_item(item)


def register():
    Miller.register(List)


if __name__ == '__main__':
    import pigui.util.pyqt5
    import about.item
    import pifou.om

    register()

    with pigui.util.pyqt5.app_context():
        path = r'c:\users\marcus\om'
        node = pifou.pom.node.Node.from_str(path)
        item = about.item.EntryItem.from_node(node)

        win = Miller()
        win.load(item)
        win.show()
        win.resize(500, 200)
