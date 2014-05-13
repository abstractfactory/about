from about.editor import dtbool
from about.editor import dtstring
from about.editor import dtint
from about.editor import dtfloat
from about.editor import dttext
from about.editor import dtdate


# def register():
#     dtbool.register()
#     dtstring.register()
#     dtint.register()
#     dtfloat.register()
#     dttext.register()
#     dtdate.register()


mapping = {
    'string': dtstring,
    'bool': dtbool,
    'int': dtint,
    'float': dtfloat,
    'text': dttext,
    'date': dtdate
}


def get(predicate):
    if not isinstance(predicate, basestring):
        predicate = predicate.type
    mod = mapping.get(predicate)
    return getattr(mod, 'Family', None)
