from pigui.pyqt5.event import BaseEvent, Type


class PathEvent(BaseEvent):
    def __init__(self, path):
        super(PathEvent, self).__init__()
        self.path = path


@Type.register
class OpenInExplorerEvent(PathEvent):
    pass


# @Type.register
# class EditEvent(PathEvent):
#     pass


@Type.register
class NothingToSaveEvent(BaseEvent):
    pass


@Type.register
class SavedEvent(BaseEvent):
    pass


@Type.register
def DataAddedEvent(PathEvent):
    def __init__(self, widget):
        super(DataAddedEvent, self).__init__()
        self.widget = widget
