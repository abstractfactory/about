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
import pigui.pyqt5.util

# Local library
import about.controller


def main(path, debug=False):
    if debug:
        pifou.setup_log()
        pigui.setup_log()

        import logging
        import openmetadata

        log = pigui.setup_log()
        log.setLevel(logging.DEBUG)

        log = pifou.setup_log()
        log.setLevel(logging.DEBUG)

        log = openmetadata.setup_log()
        log.setLevel(logging.DEBUG)

    with pigui.pyqt5.util.application_context():
        model = about.model.Model()
        win = about.controller.About()
        win.set_model(model)
        win.resize(*about.settings.WINDOW_SIZE)
        win.show()

        model.setup(path)


if __name__ == '__main__':
    main(r'c:\users\marcus\om', debug=True)
    # main(r'C:\Users\marcus\Dropbox\Apps')
    # main(r'S:\content\jobs\machine')
