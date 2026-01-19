from typing import TYPE_CHECKING
import vtk
from PySide6.QtWidgets import QWidget
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from yapfc.MouseInteractorStyle import MouseInteractorStyle
from yapfc.enums.SelectionCategory import SelectionCategory
from yapfc.util import timeit
if TYPE_CHECKING:
    from yapfc.MainWindow import MainWindow


class vtkViewer(QWidget):
    def __init__(self, parent: 'MainWindow'):
        super().__init__()
        self.pparent = parent
        # vtk initialization
        self.QVTKRenderWindowInteractor = QVTK.QVTKRenderWindowInteractor
        self.renderer = vtk.vtkRenderer()
        self.TrihedronPos = 1
        '''1 = Lower Left , 2 = Lower Right'''
        self.ShowEdges = True
        self.selectionFilter:SelectionCategory = SelectionCategory(1)
        self.cellSelection: dict[int, tuple[float]] = {}
        self.nodeSelection: list[int] = []
        self.edgeSelection: list[int] = []
        self.surfaceSelection: list[int] = []
        self.volumeSelection: list[int] = []
        self.selectionCreatedActors: dict[int, vtk.vtkActor] = {}

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

    def AddActor(self, pvtkActor, edgeVisible: bool = True):
        if self.ShowEdges and edgeVisible:
            pvtkActor.GetProperty().EdgeVisibilityOn()
        self.renderer.AddActor(pvtkActor)

    def RemoveActor(self, pvtkActor):
        self.renderer.RemoveActor(pvtkActor)

    def GetAllActors(self) -> list[vtk.vtkActor]:
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
            actor:vtkActor = self.renderer.GetActors().GetItemAsObject(i) #type:ignore
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

    def getSelection(self, filter:SelectionCategory) -> list[int]:
        match filter:
            case SelectionCategory.Nodes:
                return self.nodeSelection
            case SelectionCategory.Edges:
                return self.edgeSelection
            case SelectionCategory.Elements:
                return list(self.cellSelection.keys())
            case SelectionCategory.Surfaces:
                return self.surfaceSelection
            case SelectionCategory.Volumes:
                return self.volumeSelection
            case _:
                return self.nodeSelection

    def changeInSelection(self, idx:int, selectionType:SelectionCategory) -> None:
        try:
            mesh = self.pparent.mesh
        except AttributeError as e:
            print(f'No Mesh is loaded')
            return
        match selectionType:
            case SelectionCategory.Elements:
                elSel: dict[int, tuple] = self.cellSelection
                if idx != -1:
                    if idx not in elSel.keys():
                        elSel[idx] = mesh.getCellColor(idx)
                        mesh.setCellColor(idx, (255, 0, 0))
                        print(f'Element {idx} is selected')
                    elif idx in elSel:
                        mesh.setCellColor(idx, *elSel[idx])
                        elSel.pop(idx)
                        print(f'Element {idx} is no longer selected')
                else:
                    for i, v in zip(elSel.keys(), elSel.values()):
                        mesh.setCellColor(i, *v)
                    elSel.clear()
                    print('All elements removed from selection')
            case SelectionCategory.Nodes:
                sel:list[int] = self.nodeSelection
                actSel: dict[int, vtk.vtkActor] = self.selectionCreatedActors
                if idx != -1:
                    if idx not in sel:
                        sel.append(idx)
                        sphere_source = vtk.vtkSphereSource()
                        sphere_actor = vtk.vtkActor()
                        sphere_mapper = vtk.vtkPolyDataMapper()
                        sphere_source.SetCenter(mesh.getNodeCoords(idx))
                        sphere_source.SetRadius(0.5)  # Adjust radius as needed
                        sphere_source.Update()
                        sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())
                        sphere_actor.PickableOff()
                        sphere_actor.SetMapper(sphere_mapper)
                        sphere_actor.GetProperty().SetColor(1, 0, 0)  # Red color for visibility
                        self.AddActor(sphere_actor, edgeVisible=False)
                        actSel[idx] = sphere_actor
                        print(f'Node {idx} is selected')
                    elif idx in sel:
                        sel.remove(idx)
                        self.RemoveActor(actSel[idx])
                        actSel.pop(idx)
                        print(f'Node {idx} is no longer selected')
                else:
                    sel.clear()
                    for i in actSel.keys():
                        self.RemoveActor(actSel[i])
                    actSel.clear()
                    print('All nodes removed from selection')
            case SelectionCategory.Edges:
                pass
            case SelectionCategory.Surfaces:
                pass
            case SelectionCategory.Volumes:
                pass

    def setSelectionCategory(self, filter:int) -> None:
        self.selectionFilter = SelectionCategory(filter)
        print(f'Filter changed to {self.selectionFilter}')