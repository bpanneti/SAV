import sys
from os.path import join, dirname, abspath
import PyQt5
import platform

QT_VERSION = tuple(int(v) for v in PyQt5.QtCore.QT_VERSION_STR.split('.'))
""" tuple: Qt version. """

PLATFORM = platform.system()


def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return join(sys._MEIPASS, dirname(abspath(__file__)), relative_path)
    return join(dirname(abspath(__file__)), relative_path)
