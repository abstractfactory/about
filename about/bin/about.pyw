
import os
import sys


def add_to_path():
    root = os.path.abspath(__file__)
    for x in range(3):
        root = os.path.dirname(root)
    sys.path.insert(0, root)
    print "I: adding %r to PYTHONPATH" % root


def get_path():
    try:
        path = sys.argv[1]
        print "I: Using ARGS"
    except:
        path = os.getcwd()
        print "I: Using CWD"

    # For now, don't bother with trying to add
    # metadata to files.
    if os.path.isfile(path):
        path = os.path.dirname(path)

    return path


def init_cwd():
    # Make working directory local to About,
    # regardless of where this executable is being run from.
    # (This is important for local stylesheets to have any effect)
    working_directory = os.path.dirname(about.presentation.__file__)
    os.chdir(working_directory)


if __name__ == '__main__':
    message = '''
 _____________
|             |
| About 0.5.2 |
|_____________|

Press CTRL-C to quit..

-----------------------
'''
    print message
    add_to_path()

    import about.presentation
    path = get_path()
    init_cwd()

    print "I: running About @ %r" % path
    about.presentation.main(path)
