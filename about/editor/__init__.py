
def register():
    from piapp.about.editor import dtbool
    from piapp.about.editor import dtstring
    from piapp.about.editor import dtint
    from piapp.about.editor import dtfloat
    from piapp.about.editor import dttext
    from piapp.about.editor import dtdate

    dtbool.register()
    dtstring.register()
    dtint.register()
    dtfloat.register()
    dttext.register()
    dtdate.register()
