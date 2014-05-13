
import openmetadata as om
from openmetadata import service


def exists(node):
    return service.exists(node.path.as_str)


def push(node):
    pass


def pull(node,
         depth=1,  # NotImplemented
         lazy=False,
         merge=False,
         overwrite=True,
         service=None):  # NotImplemented

    """Populate .data container of `node`"""

    # if exists(node):
    location, metapath = om.split(node.path.as_str)
    metadata = om.read(location, metapath, convert=False)

    if isinstance(metadata, list):

        if not merge:
            node.children.clear()

        for entry in metadata:
            child = node.copy(path=entry.path)
            node.children.add(child)
            node.data['entry'] = entry
    else:
        if lazy and 'value' in node.data:
            return node

        if overwrite or not 'value' in node.data:
            if metadata:
                value = metadata.value
            else:
                # Get default value
                value = om.Entry(node.path.basename).value
            node.data['value'] = value

    return node
