
# # import pigui.delegate
# import about.delegate

# from PyQt5 import QtWidgets
# from PyQt5 import QtCore


# class BoolDelegate(about.delegate.EditorDelegate):
#     def __init__(self, *args, **kwargs):
#         super(BoolDelegate, self).__init__(*args, **kwargs)

#         state = self.getdata()
#         self.widget.checkbox.setChecked(state)
#         self.widget.checkbox.stateChanged.connect(self.modified_event)

#     def modified_event(self, state):
#         self.event.emit(name='modified',
#                         data=[True if state else False, self])

    


# class BoolWidget(QtWidgets.QWidget):
#     def __init__(self, *args, **kwargs):
#         super(BoolWidget, self).__init__(*args, **kwargs)
#         self.setAttribute(QtCore.Qt.WA_StyledBackground)

#         checkbox = QtWidgets.QCheckBox()

#         layout = QtWidgets.QHBoxLayout(self)
#         layout.addWidget(checkbox)
#         layout.setContentsMargins(*[0]*4)
#         layout.setAlignment(QtCore.Qt.AlignRight)

#         self.checkbox = checkbox


# class BoolFamily(object):
#     predicate = 'bool'
#     DelegateClass = BoolDelegate
#     WidgetClass = BoolWidget


# def register():
#     about.delegate.EditorDelegate.register(BoolFamily)
