import sys

from PySide6.QtWidgets import QApplication

from vtkmodules.vtkRenderingCore import vtkRenderer, vtkPolyDataMapper, vtkActor, vtkPointPicker
from vtkmodules.vtkFiltersSources import vtkConeSource
from vtkmodules.qt import QVTKRenderWindowInteractor as QVTK


if __name__ == '__main__':

    # DOESN'T WORK!!!!!!!!!!!

    # every QT app needs an app
    app = QApplication(['QVTKRenderWindowInteractor'])

    # create the widget
    widget = QVTK.QVTKRenderWindowInteractor()
    widget.Initialize()
    widget.Start()

    # if you dont want the 'q' key to exit comment this.
    widget.AddObserver("ExitEvent", lambda o, e, a=app: a.quit())

    ren = vtkRenderer()
    widget.GetRenderWindow().AddRenderer(ren)

    cone = vtkConeSource()
    cone.SetResolution(8)

    coneMapper = vtkPolyDataMapper()
    coneMapper.SetInputConnection(cone.GetOutputPort())

    coneActor = vtkActor()
    coneActor.SetMapper(coneMapper)

    ren.AddActor(coneActor)

    widget.SetPicker(vtkPointPicker())

    # show the widget
    widget.show()

    # start event processing
    sys.exit(app.exec())
