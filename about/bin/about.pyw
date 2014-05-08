#!python

"""Main entry point for build"""

import os
import sys

# check_dependencies()

# ------------------------------------------------------------


import pifou
if pifou.missing_dependencies:
    import pifou.error
    raise pifou.error.Dependency(pifou.missing_dependencies)

from piapp.about import presentation

# Make working directory local to About,
# regardless of where this executable is being run from.
# (This is important for local stylesheets to have any effect)
working_directory = os.path.dirname(presentation.__file__)
os.chdir(working_directory)


try:
    path = sys.argv[1]
except:
    path = os.getcwd()


if __name__ == '__main__':
    presentation.main(path)
