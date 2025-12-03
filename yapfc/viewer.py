from PySide6.QtWidgets import QWidget, QMainWindow
import vtk
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCellPicker,
    vtkDataSetMapper,
)

class MouseInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(self, parent:'vtkViewer'):
        self.AddObserver('LeftButtonPressEvent', self.left_button_press_event)
        self.parent = parent
        self.selected_mapper = vtkDataSetMapper()
        self.selected_actor = vtkActor()

    def highlightCell(self, cellID:int) -> None:
        mesh = self.parent.parent.mesh.getMesh()
        # Create a color array for cells
        colors = vtk.vtkUnsignedCharArray()
        colors.SetNumberOfComponents(3)  # RGB
        colors.SetName("CellColors")
        
        # Assign a color to each cell (cube has 6 faces)
        for i in range(mesh.GetNumberOfCells()):
            if i == cellID:
                colors.InsertNextTuple3(255, 0, 0)
            else:  # Red
                colors.InsertNextTuple3(255, 255, 255)
    
        # Add the color array to cell data
        mesh.GetCellData().SetScalars(colors)

    def left_button_press_event(self, obj, event):
        # Get the location of the click (in window coordinates)
        pos = self.GetInteractor().GetEventPosition()

        picker = vtkCellPicker()
        picker.SetTolerance(0.0005)

        # Pick from this location.
        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())

        world_position = picker.GetPickPosition()

        if picker.GetCellId() != -1:
            print(f'''Pick position is: ({world_position[0]:.6g},
                  {world_position[1]:.6g}, {world_position[2]:.6g})''')
            print(f'Cell id is: {picker.GetCellId()}')

        self.highlightCell(picker.GetCellId())
        # Forward events
        self.OnLeftButtonDown()


class vtkViewer(QWidget):
    def __init__(self, parent:'MainWindow'):
        super().__init__()
        self.parent:'MainWindow' = parent
        # vtk initialization
        self.QVTKRenderWindowInteractor = QVTK.QVTKRenderWindowInteractor
        self.renderer = vtk.vtkRenderer()
        self.TrihedronPos = 1
        '''1 = Lower Left , 2 = Lower Right'''
        self.ShowEdges = True

        # Set background color of the renderer
        self.renderer.SetBackground(0.2, 0.3, 0.4)  # RGB color
        self.interactor = self.QVTKRenderWindowInteractor(self)
        self.trackball = MouseInteractorStyle(self)
        self.trackball.SetDefaultRenderer(self.renderer)
        self.interactor.SetInteractorStyle(self.trackball)
        self.interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor.GetRenderWindow().PointSmoothingOn()
        self.interactor.GetRenderWindow().LineSmoothingOn()
        self.interactor.Initialize()
        self.interactor.Start()

        #Setup Trihedron
        self.Trihedron = self.MakeAxesActor()
        self.om1 = vtk.vtkOrientationMarkerWidget()
        self.om1.SetOrientationMarker(self.Trihedron)
        self.om1.SetInteractor(self.interactor)
        self.om1.EnabledOn()
        self.om1.InteractiveOff()

    def UpdateView(self):
        self.interactor.ReInitialize()
        self.interactor.GetRenderWindow().Render()
        self.repaint()

    def paintEvent(self, ev):
        size = self.size()
        self.interactor.GetRenderWindow().SetSize(size.width(), size.height())

    def MakeAxesActor(self):
        axes = vtk.vtkAxesActor()
        axes.SetShaftTypeToCylinder()
        axes.SetXAxisLabelText('X')
        axes.SetYAxisLabelText('Y')
        axes.SetZAxisLabelText('Z')
        axes.SetTotalLength(1.5, 1.5, 1.5)
        axes.SetCylinderRadius(0.5 * axes.GetCylinderRadius())
        axes.SetConeRadius(1.025 * axes.GetConeRadius())
        axes.SetSphereRadius(1.5 * axes.GetSphereRadius())
        return axes

    def ResizeTrihedron(self, width, height):
        if self.Trihedron:
            if (width == 0):
                width = 100
            if (height == 0):
                height = 100

            if self.TrihedronPos == 1:  # Position lower Left in the viewport.
                self.om1.SetViewport(0, 0, (200.0 / width), (200.0 / height))

            if self.TrihedronPos == 2:  # Position lower Right in the viewport.
                self.om1.SetViewport(1 - (200.0 / width),
                                     0, 1, (200.0 / height))

    def resizeEvent(self, ev):
        self.interactor.GetRenderWindow().SetSize(self.size().width(),
                                                  self.size().height())
        self.ResizeTrihedron(self.size().width(), self.size().height())

    def ResetCamera(self):
        self.renderer.ResetCamera()
        self.camera = self.renderer.GetActiveCamera()
        self.camera.ParallelProjectionOn()

    def AddActor(self, pvtkActor):
        if self.ShowEdges:
            pvtkActor.GetProperty().EdgeVisibilityOn()

        self.renderer.AddActor(pvtkActor)
        self.ResetCamera()

    def RemoveActor(self, pvtkActor):
        self.renderer.RemoveActor(pvtkActor)
        self.ResetCamera()

    def GetAllActors(self) -> list[vtkActor]:
        """Return a list of all vtkActors currently in the renderer."""
        actors = []
        num_actors = self.renderer.GetActors().GetNumberOfItems()
        for i in range(num_actors):
            actor = self.renderer.GetActors().GetItemAsObject(i)
            actors.append(actor)
        return actors

    def SetRepresentation(self, aTyp):
        ''' aTyp = 1 - Points
            aTyp = 2 - Wireframe
            aTyp = 3 - Surface
            aTyp = 4 - Surface with edges
        '''
        num_actors = self.renderer.GetActors().GetNumberOfItems()
        for i in range(num_actors):
            actor = self.renderer.GetActors().GetItemAsObject(i)
            if (aTyp == 1):
                actor.GetProperty().SetRepresentationToPoints()
                actor.GetProperty().SetPointSize(4.0)
                self.ShowEdges = False

            if (aTyp == 2):
                actor.GetProperty().SetRepresentationToWireframe()
                self.ShowEdges = False

            if (aTyp == 3):
                actor.GetProperty().SetRepresentationToSurface()
                actor.GetProperty().EdgeVisibilityOff()
                self.ShowEdges = False

            if (aTyp == 4):
                actor.GetProperty().SetRepresentationToSurface()
                actor.GetProperty().EdgeVisibilityOn()
                self.ShowEdges = True

        self.UpdateView()
