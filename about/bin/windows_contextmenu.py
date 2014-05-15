"""

Description
    Generate registry patch for adding "Open in About"
    to the Windows right-click menu.

"""

template = r'''Windows Registry Editor Version 5.00

[HKEY_CLASSES_ROOT\Directory\shell\About]
@="Open in &About"

[HKEY_CLASSES_ROOT\Directory\shell\About\command]
@="{executable} {about_dir}\\bin\\about.pyw \"%1\""

'''

import os
import sys

basename = os.path.basename(__file__)


def add_to_path():
    root = os.path.abspath(__file__)
    for x in range(3):
        root = os.path.dirname(root)
    sys.path.insert(0, root)
    print "I: adding %r to PYTHONPATH" % root


def generate():
    import about

    python_dir = os.path.dirname(sys.executable)
    pythonw_exec = os.path.join(python_dir, 'pythonw.exe')
    pythonw_exec = pythonw_exec.replace('\\', '\\' * 2)
    about_dir = os.path.dirname(about.__file__)
    about_dir = about_dir.replace('\\', '\\' * 2)

    patch = template.format(
        executable=pythonw_exec,
        about_dir=about_dir)

    name, ext = os.path.splitext(basename)
    output_dir = os.path.dirname(__file__)
    output_file = os.path.join(output_dir, '%s.reg' % name)

    with open(output_file, 'w') as f:
        f.write(patch)

    return output_file


def confirm():
    comparison = os.path.join('about',
                              'bin',
                              basename)

    if not __file__.endswith(comparison):
        raise ValueError("""{line}
Fatal

Make sure you run from original directory:

    ..{comp}

{line}
""".format(line='-' * 60,
           comp=comparison))


def main():
    add_to_path()
    output = generate()
    sys.stdout.write('''
{line}

Successfully generated patch at:

    {path}

Double-click on this, and you're done!

{line}

'''.format(line='-' * 60,
           path=('..' + output[-50:]) if len(output) > 50 else output))


if __name__ == '__main__':
    import time

    try:
        confirm()
        main()
    except ValueError as e:
        sys.stderr.write(str(e))

    sys.stdout.write("Press CTRL-C or close this window to continue")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
