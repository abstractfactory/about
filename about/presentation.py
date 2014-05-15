"""Main entry-point for About
https://github.com/abstractfactory/about

Dependencies
                 _____________     __________________
                |             |   |                  |
                |  widget.py  |   |  application.py  |
                |_____________|   |__________________|
                       |                    |
                       |____________________|
                                |
            _________        ___v____
           |         |      |        |
           |  pifou  |----->|  this  |
           |_________|      |        |
                            |        |
            _________       |        |
           |         |      |        |
           |  pigui  |----->|        |
           |_________|      |________|

"""

# pifou library
import pifou
import pifou.pom.node

# pigui library
import pigui
import pigui.util.pyqt5

# Local library
import about.widget
import about.application


def main(path, debug=False):
    if debug:
        pifou.setup_log()
        pigui.setup_log()

    node = pifou.pom.node.Node.from_str(path)
    widget = about.widget.About
    app = about.application.About(widget)

    # with pigui.util.pyqt5.app_context(use_baked_css=True):
    with pigui.util.pyqt5.app_context():
        app.init_widget()
        app.load(node)


if __name__ == '__main__':
    main(r'c:\users\marcus\om', debug=True)
    # main(r'C:\Users\marcus\Dropbox\Apps')
    # main(r'S:\content\jobs\machine')
