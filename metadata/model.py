from __future__ import unicode_literals, print_function
from atom.api import Atom, List, Int, observe
import enaml
from enaml.qt.qt_application import QtApplication


class Metadata(Atom):
    curve_id = Int()
    attributes = List()

def main():
    with enaml.imports():
        from view import MetaDataView

    curve = Metadata(curve_id=123, attributes=['gas', 'NBP'])

    app = QtApplication()
    v = MetaDataView(curve=curve)
    v.show()

    app.start()

if __name__ == '__main__':
    main()