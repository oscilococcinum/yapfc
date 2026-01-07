from PySide6.QtWidgets import QMainWindow, QStatusBar, QVBoxLayout, QDockWidget, QTreeView, QMenu, QInputDialog, QFileDialog, QWidget
from PySide6.QtGui import  QAction, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QPoint, QObject, QModelIndex
from yapfc.model import (
    CcxWriter, MeshSubWriter, MaterialSubWriter,
    SectionSubWriter, ConstraintSubWriter, ContactSubWriter,
    AmplitudeSubWriter, InitialConditionSubWriter, StepSubWriter,
    Label, AnalysisSubWriter, BoundarySubWriter
)
import vtk
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkCellPicker,
    vtkPointPicker,
    vtkPicker,
    vtkDataSetMapper,
)
from typing import Any, cast, List
from enum import Enum, auto
import numpy as np
from yapfc.mesh import Mesh
from yapfc.runner import run_script, save_inp_file, open_paraview
from yapfc.dialogs import OptionsDialog, get_option_from_json

class Tools(Enum):
    Options = 0

class Selection(Enum):
    Elements = 0
    Nodes = 1
    Edges = 2
    Surfaces = 3
    Volumes = 4

class SelectionFilter(Enum):
    Elements = 0
    Nodes = 1
    Edges = 2
    Surfaces = 3
    Volumes = 4

def isInsOrSubclsIns(obj:Any, cls:type) -> bool:
    if isinstance(obj, cls) or issubclass(type(obj), cls):
        return True
    else:
        return False

def collect_components(item):
    components = [item]  # Start with the current item

    if item.hasChildren():
        for row in range(item.rowCount()):
            child_item = item.child(row)
            components.extend(collect_components(child_item))  # Recursive call

    return components

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mesh:Mesh
        self.options = OptionsDialog(self)

        self.setWindowTitle("yapfc")
        self.setGeometry(100, 100, 800, 600)
        # Create the central widget
        self.central_widget = vtkViewer(self)
        self.setCentralWidget(self.central_widget)
        self.llayout = QVBoxLayout(self.central_widget)
        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        # Create_menus
        self.menu_bar = self.menuBar()

        self.file_menu = self.menu_bar.addMenu("File")
        self.open_action = QAction("Open", self)
        self.open_action.triggered.connect(lambda: self.central_widget.AddActor(self.open_mesh()))
        self.save_action = QAction("Save", self)
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.close)
        self.file_menu.addAction(self.open_action)
        self.file_menu.addAction(self.save_action)
        self.close_action = QAction("Close", self)
        self.close_action.triggered.connect(lambda: self.central_widget.RemoveActor(self.central_widget.GetAllActors()[0]))
        self.file_menu.addAction(self.close_action)
        self.file_menu.addAction(self.exit_action)

        self.edit_menu = self.menu_bar.addMenu("Edit")
        self.undo_action = QAction("Undo", self)
        self.redo_action = QAction("Redo", self)
        self.edit_menu.addAction(self.undo_action)
        self.edit_menu.addAction(self.redo_action)

        self.view_menu = self.menu_bar.addMenu("View")

        self.wireframe_rep = QAction("Wireframe", self)
        self.wireframe_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(2))
        self.view_menu.addAction(self.wireframe_rep)

        self.points_rep = QAction("Points", self)
        self.points_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(1))
        self.view_menu.addAction(self.points_rep)

        self.surface_rep = QAction("Surface", self)
        self.surface_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(3))
        self.view_menu.addAction(self.surface_rep)

        self.surface_edges_rep = QAction("Surface with edges", self)
        self.surface_edges_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(4))
        self.view_menu.addAction(self.surface_edges_rep)


        # Selection
        self.selection_menu = self.menu_bar.addMenu("Selection")
        self.selection_menu.addActions([QAction(item.name, self) for item in Selection])
        [item.triggered.connect(lambda _, idx=index: self.central_widget.setSelectionFilter(Selection(idx).value)) for index, item in enumerate(self.selection_menu.actions())]

        # Tools
        self.tools_menu = self.menu_bar.addMenu("Tools")
        self.tools_menu.addActions([QAction(item.name, self) for item in Tools])
        self.tools_menu.actions()[Tools.Options.value].triggered.connect(self.open_options_dialog)

        # Help
        self.help_menu = self.menu_bar.addMenu("Help")
        self.about_action = QAction("About", self)
        self.help_menu.addAction(self.about_action)

        # Create a dock widget for the tree view
        self.dock_widget = QDockWidget("Simulation Components", self)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea, self.dock_widget)
        # Create the tree view
        self.tree_view = QTreeView()
        self.dock_widget.setWidget(self.tree_view)
        # Set up a standard item model
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(["Components"])
        self.tree_view.setModel(self.model)
        # Add a root writers
        self.model_item = Label("Model")
        self.meshes = Label("Meshes")
        self.materials = Label("Materials")
        self.sections = Label("Sections")
        self.constraints = Label("Constraints")
        self.contacts = Label("Contacts")
        self.amplitudes = Label("Amplitudes")
        self.initial_conditions  = Label("Initial Conditions")
        self.steps = Label("Steps")
        self.analyses = Label("Analyses")
        self.model.appendRow(self.model_item)
        self.model_item.appendRow(self.meshes)
        self.model_item.appendRow(self.materials)
        self.model_item.appendRow(self.sections)
        self.model_item.appendRow(self.constraints)
        self.model_item.appendRow(self.contacts)
        self.model_item.appendRow(self.amplitudes)
        self.model_item.appendRow(self.initial_conditions)
        self.model_item.appendRow(self.steps)
        self.model.appendRow(self.analyses)
        self.tree_view.expandAll()
        # Connect double-click signal
        self.tree_view.doubleClicked.connect(self.double_click_on_writer)
        # Set up context menu
        self.tree_view.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.open_context_menu)

    def open_file_dialog(self):
        options = QFileDialog()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;STL Files (*.stl);;Mesh Files (*.mesh);;Msh Files (*.msh)", options=options.options())
        return file_name

    def double_click_on_writer(self, index):
        item = self.model.itemFromIndex(index)
        if isinstance(item, CcxWriter):
            item.doubleClicked()

    def open_context_menu(self, position: QPoint):
        indexes:'list[QModelIndex]' = self.tree_view.selectedIndexes()
        if indexes:
            selected_item:Any = self.model.itemFromIndex(indexes[0])
        else:
            return

        selected_item_class: str = selected_item.getTextLabel()
        if selected_item_class.endswith("ses"):
            selected_item_class = selected_item_class.removesuffix("es")
            selected_item_class = selected_item_class + "is"
        elif selected_item_class.endswith("es"):
            selected_item_class = selected_item_class.removesuffix("es")
        elif selected_item_class.endswith("s"):
            selected_item_class = selected_item_class.removesuffix("s")

        menu = QMenu()
        addItem = QAction(f"Add {selected_item_class}", self)
        addBoundary = QAction(f"Add {selected_item_class}", self)
        removeItem = QAction(f"Remove {selected_item_class}", self)
        openTextEdit = QAction(f"Text edit {selected_item_class}", self)
        runAnalysis = QAction("Run Analysis", self)
        showResults = QAction("Show Results", self)

        match selected_item.getTextLabel():
            case "Meshes":
                menu.addAction(addItem)
                menu.addAction(openTextEdit)
            case "Materials":
                menu.addAction(addItem)
                menu.addAction(openTextEdit)
            case "Sections":
                menu.addAction(addItem)
                menu.addAction(openTextEdit)
            case "Contacts":
                menu.addAction(addItem)
                menu.addAction(openTextEdit)
            case "Initial Conditions":
                menu.addAction(addItem)
                menu.addAction(openTextEdit)
            case "Steps":
                menu.addAction(addItem)
                menu.addAction(openTextEdit)
            case "Analyses":
                menu.addAction(addItem)
                menu.addAction(openTextEdit)
            case "Mesh":
                menu.addAction(removeItem)
                menu.addAction(openTextEdit)
            case "Material":
                menu.addAction(removeItem)
                menu.addAction(openTextEdit)
            case "Section":
                menu.addAction(removeItem)
                menu.addAction(openTextEdit)
            case "Contact":
                menu.addAction(removeItem)
                menu.addAction(openTextEdit)
            case "Initial Condition":
                menu.addAction(removeItem)
                menu.addAction(openTextEdit)
            case "Step":
                menu.addAction(addBoundary)
                menu.addAction(removeItem)
            case "Analysis":
                menu.addAction(runAnalysis)
                menu.addAction(showResults)
                menu.addAction(removeItem)

        addItem.triggered.connect(lambda: self.addItem(selected_item))
        addBoundary.triggered.connect(lambda: self.addBoundary(selected_item))
        removeItem.triggered.connect(lambda: self.removeItem(selected_item))
        openTextEdit.triggered.connect(lambda: self.openTextEdit(selected_item))
        runAnalysis.triggered.connect(lambda: self.runAnalysis())
        showResults.triggered.connect(lambda: self.show_results())

        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def open_mesh(self):
        fpath = self.open_file_dialog()
        self.mesh = Mesh(fpath)
        return self.mesh.getActor()

    def addItem(self, parent_item):
        parent_class: str = parent_item.getTextLabel()
        text, ok = QInputDialog.getText(self, f"Add {parent_class}", "Enter item name:")
        if ok and text:
            match parent_class:
                case "Meshes": new_item = MeshSubWriter(text)
                case "Materials": new_item = MaterialSubWriter(text)
                case "Sections": new_item = SectionSubWriter(text)
                case "Constraints": new_item = ConstraintSubWriter(text)
                case "Contacts": new_item = ContactSubWriter(text)
                case "Amplitudes": new_item = AmplitudeSubWriter(text)
                case "Initial Conditions": new_item = InitialConditionSubWriter(text)
                case "Steps": new_item = StepSubWriter(text)
                case "Analyses": new_item = AnalysisSubWriter(text)

            parent_item.appendRow(new_item) #type:ignore

    def addBoundary(self, parent_item: QStandardItem):
        if parent_item.hasChildren(): nextIndex: int = parent_item.rowCount()
        else: nextIndex: int = 0
        text, ok = QInputDialog.getText(self, "Add Boundary", "Enter item name:", text=f"Boundary{nextIndex}")
        if ok and text:
            new_item = BoundarySubWriter(text)
            parent_item.appendRow(new_item)

    def removeItem(self, item: CcxWriter):
        if item.parent():
            item.parent().removeRow(item.row())
        else:
            self.model.removeRow(item.row())
        try:
            item.removeWriter()
        except:
            print(f'Unable to remove this writter - {item.getTextLabel()}')

    def openTextEdit(self, item: CcxWriter):
        item.openTextEditor()

    def runAnalysis(self):
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            selected_item:Label = self.model.itemFromIndex(indexes[0]) #type:ignore

            inp_list: list[str] = []
            inp_text: str = ""
            comp: list[Label] = collect_components(self.model_item)
            for label in comp:
                try:
                    inp_list.append(label.getStoredText())
                except:
                    pass

            for x in inp_list:
                inp_text = inp_text + '\n' + x
            print(inp_text)

            save_inp_file(inp_text, selected_item.text())
            run_script(get_option_from_json("options.json", "ccx_path"), selected_item.text())
    
    def show_results(self) -> None:
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            selected_item = self.model.itemFromIndex(indexes[0])
            open_paraview(get_option_from_json("options.json", "paraview_path"), f"{selected_item.text()}.exo")
    
    def open_options_dialog(self) -> None:
        self.options.exec()

class MouseInteractorStyle(vtkInteractorStyleTrackballCamera):
    def __init__(self, parent:'vtkViewer'):
        self.AddObserver('LeftButtonPressEvent', self.left_button_press_event) #type:ignore
        self.parent = parent
        self.selected_mapper = vtkDataSetMapper()
        self.selected_actor = vtkActor()

    def left_button_press_event(self, obj, event):
        match self.parent.selectionFilter:
            case SelectionFilter.Elements:
                self.pickCell()
            case SelectionFilter.Nodes:
                self.nodePick()
            case SelectionFilter.Edges:
                self.edgePick()
            case SelectionFilter.Surfaces:
               self.surfacePick() 
            case SelectionFilter.Volumes:
                self.volumePick()
        self.OnLeftButtonDown()

    def pickCell(self) -> None:
        pos = self.GetInteractor().GetEventPosition()

        picker = vtkCellPicker()
        picker.SetTolerance(0.0005)

        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())

        world_position = picker.GetPickPosition()

        cellId:int = picker.GetCellId()

        if cellId != -1:
            print(f'''Pick position is: ({world_position[0]:.6g}, {world_position[1]:.6g}, {world_position[2]:.6g})''')
            print(f'Cell id is: {cellId}')
            self.parent.appendSelection(cellId, SelectionFilter.Elements)
        else:
            self.parent.clearSelection(SelectionFilter.Elements)
            print('Selection clean')
    
    def nodePick(self) -> None:
        pos = self.GetInteractor().GetEventPosition()

        picker = vtkCellPicker()
        picker.SetTolerance(0.0005)

        picker.Pick(pos[0], pos[1], 0, self.GetDefaultRenderer())

        world_position = picker.GetPickPosition()

        pointId:int = picker.GetPointId()

        if pointId != -1:
            print(f'''Pick position is: ({world_position[0]:.6g}, {world_position[1]:.6g}, {world_position[2]:.6g})''')
            print(f'Point id is: {pointId}')
            self.parent.appendSelection(pointId, SelectionFilter.Nodes)
        else:
            self.parent.clearSelection(SelectionFilter.Nodes)
            print('Selection clean')

    def edgePick(self) -> None:
        pass

    def surfacePick(self) -> None:
        pass

    def volumePick(self) -> None:
        pass

class vtkViewer(QWidget):
    def __init__(self, parent:MainWindow):
        super().__init__()
        self.pparent = parent
        # vtk initialization
        self.QVTKRenderWindowInteractor = QVTK.QVTKRenderWindowInteractor
        self.renderer = vtk.vtkRenderer()
        self.TrihedronPos = 1
        '''1 = Lower Left , 2 = Lower Right'''
        self.ShowEdges = True
        self.selectionFilter:SelectionFilter = SelectionFilter(1)
        self.cellSelection:list = []
        self.nodeSelection:list = []
        self.edgeSelection:list = []
        self.surfaceSelection:list = []
        self.volumeSelection:list = []

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

    def getSelection(self, filter:SelectionFilter) -> list[int]:
        match filter:
            case SelectionFilter.Nodes:
                return self.nodeSelection
            case SelectionFilter.Edges:
                return self.edgeSelection
            case SelectionFilter.Elements:
                return self.cellSelection
            case SelectionFilter.Surfaces:
                return self.surfaceSelection
            case SelectionFilter.Volumes:
                return self.volumeSelection
            case _:
                return self.nodeSelection

    def appendSelection(self, idx:int, selectionType:SelectionFilter) -> None:
        match selectionType:
            case SelectionFilter.Elements:
                sel:list[int] = self.cellSelection
                if idx not in sel:
                    sel.append(idx)
                    self.highlightSelection(selectionType)
                else:
                    print('No change in cell selection')
            case SelectionFilter.Nodes:
                sel:list[int] = self.nodeSelection
                if idx not in sel:
                    sel.append(idx)
                    self.highlightSelection(selectionType)
                else:
                    print('No change in selection')
            case SelectionFilter.Edges:
                sel:list[int] = self.edgeSelection
                if idx not in sel:
                    sel.append(idx)
                    self.highlightSelection(selectionType)
                else:
                    print('No change in selection')
            case SelectionFilter.Surfaces:
                sel:list[int] = self.surfaceSelection
                if idx not in sel:
                    sel.append(idx)
                    self.highlightSelection(selectionType)
                else:
                    print('No change in selection')
            case SelectionFilter.Volumes:
                sel:list[int] = self.volumeSelection
                if idx not in sel:
                    sel.append(idx)
                    self.highlightSelection(selectionType)
                else:
                    print('No change in selection')

    def clearSelection(self, selectionType:SelectionFilter) -> None:
        selection:list[int] = self.getSelection(selectionType)
        match selectionType:
            case SelectionFilter.Nodes:
                pass
            case SelectionFilter.Edges:
                pass
            case SelectionFilter.Elements:
                try:
                    mesh = self.pparent.mesh.getMesh()
                    colors:vtk.vtkUnsignedCharArray = self.pparent.mesh.getMesh().GetCellData().GetScalars('CellColors')
                
                    for i in selection:
                        colors.SetTuple3(i, 255, 255, 255)
                        print(colors.GetTuple3(i))
                
                    mesh.GetCellData().SetScalars(colors)
                    mesh.GetCellData().SetActiveScalars('CellColors')
                    selection.clear()
                except:
                    print('Clear of selection unsuccesfull')
            case SelectionFilter.Surfaces:
                pass
            case Selection.Volumes:
                pass

    def highlightSelection(self, selectionType:SelectionFilter) -> None:
        selection:list[int] = self.getSelection(selectionType)
        match selectionType:
            case SelectionFilter.Nodes:
                pass
            case SelectionFilter.Edges:
                pass
            case SelectionFilter.Elements:
                try:
                    mesh = self.pparent.mesh.getMesh()
                    colors:vtk.vtkUnsignedCharArray = self.pparent.mesh.getMesh().GetCellData().GetScalars('CellColors')

                    for i in selection:
                        colors.SetTuple3(i, 255, 0, 0)
                        print(colors.GetTuple3(i))

                    mesh.GetCellData().SetScalars(colors)
                    mesh.GetCellData().SetActiveScalars('CellColors')
                except:
                    print('Highlight unsuccesfull')
            case SelectionFilter.Surfaces:
                pass
            case Selection.Volumes:
                pass

    def setSelectionFilter(self, filter:int) -> None:
        self.selectionFilter = SelectionFilter(filter)
        print(f'Filter changed to {self.selectionFilter}')
