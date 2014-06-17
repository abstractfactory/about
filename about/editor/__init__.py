from about.editor import dtbool
from about.editor import dtstring
from about.editor import dtint
from about.editor import dtfloat
from about.editor import dttext
# from about.editor import dtdate
from about.editor import noeditor


mapping = {
    '.string': dtstring,
    '.bool': dtbool,
    '.int': dtint,
    '.float': dtfloat,
    '.text': dttext,
    # '.date': dtdate,
    'no-editor': noeditor
}


def get(predicate):
    mod = mapping.get(predicate)
    editor = getattr(mod, 'Editor', None)
    return editor
