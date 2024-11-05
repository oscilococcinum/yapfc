from PySide6.QtWidgets import (
        QApplication, QMainWindow, QToolBar, QStatusBar, QWidget,
        QVBoxLayout, QDockWidget, QTreeView, QMenu, QInputDialog,
        QFileDialog
        )
from PySide6.QtGui import (
        QAction, QStandardItemModel, QStandardItem
        )
from PySide6.QtCore import Qt, QPoint
from .model import Writer, Step
import vtk
import vtkmodules.qt.QVTKRenderWindowInteractor as QVTK
from .mesh import load_file


class vtkViewer(QWidget):
    def __init__(self):
        super(vtkViewer, self).__init__()

        # vtk initialization
        self.QVTKRenderWindowInteractor = QVTK.QVTKRenderWindowInteractor
        self.renderer = None
        self.interactor = None
        self.TrihedronPos = 1
        '''1 = Lower Left , 2 = Lower Right'''
        self.ShowEdges = True

        self.SetupWnd()

    def SetupWnd(self):
        self.SetupRenderer()
        self.SetupTrihedron()

    def SetupRenderer(self):
        self.renderer = vtk.vtkRenderer()

        # Set background color of the renderer
        self.renderer.SetBackground(0.2, 0.3, 0.4)  # RGB color
        self.interactor = self.QVTKRenderWindowInteractor(self)
        self.trackball = vtk.vtkInteractorStyleTrackballCamera()
        self.interactor.SetInteractorStyle(self.trackball)
        self.interactor.GetRenderWindow().AddRenderer(self.renderer)
        self.interactor.GetRenderWindow().PointSmoothingOn()
        self.interactor.GetRenderWindow().LineSmoothingOn()
        self.interactor.Initialize()
        self.interactor.Start()

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

    def SetupTrihedron(self):
        self.Trihedron = self.MakeAxesActor()
        self.om1 = vtk.vtkOrientationMarkerWidget()
        self.om1.SetOrientationMarker(self.Trihedron)
        self.om1.SetInteractor(self.interactor)
        self.om1.EnabledOn()
        self.om1.InteractiveOff()

    def ResizeTrihedron(self, width, height):
        if self.Trihedron:
            if (width == 0):
                width = 100
            if (height == 0):
                height = 100

            if self.TrihedronPos == 1:  # Position lower Left in the viewport.
                self.om1.SetViewport(0, 0, (200.0 / width), (200.0 / height))

            if self.TrihedronPos == 2:  # Position lower Right in the viewport.
                self.om1.SetViewport(1 - (200.0 / width), 0, 1, (200.0 / height))

    def resizeEvent(self, ev):
        self.interactor.GetRenderWindow().SetSize(self.size().width(), self.size().height())
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

    def GetAllActors(self):
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


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        def file_menu():
            # File menu
            file_menu = self.menu_bar.addMenu("File")
            open_action = QAction("Open", self)
            open_action.triggered.connect(lambda: self.central_widget.AddActor(load_file(self.open_file_dialog())))
            save_action = QAction("Save", self)
            exit_action = QAction("Exit", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(open_action)
            file_menu.addAction(save_action)
            close_action = QAction("Close", self)
            close_action.triggered.connect(lambda: self.central_widget.RemoveActor(self.central_widget.GetAllActors()[0]))
            file_menu.addAction(close_action)
            file_menu.addAction(exit_action)

        def edit_menu():
            # Edit menu
            edit_menu = self.menu_bar.addMenu("Edit")
            undo_action = QAction("Undo", self)
            redo_action = QAction("Redo", self)
            edit_menu.addAction(undo_action)
            edit_menu.addAction(redo_action)

        def view_menu():
            # View menu
            view_menu = self.menu_bar.addMenu("View")

            wireframe_rep = QAction("Wireframe", self)
            wireframe_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(2))
            view_menu.addAction(wireframe_rep)

            points_rep = QAction("Points", self)
            points_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(1))
            view_menu.addAction(points_rep)

            surface_rep = QAction("Surface", self)
            surface_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(3))
            view_menu.addAction(surface_rep)

            surface_edges_rep = QAction("Surface with edges", self)
            surface_edges_rep.triggered.connect(lambda: self.central_widget.SetRepresentation(4))
            view_menu.addAction(surface_edges_rep)

        def tools_menu():
            # Tools menu
            tools_menu = self.menu_bar.addMenu("Tools")
            # Add tools actions here

        def help_menu():
            # Help menu
            help_menu = self.menu_bar.addMenu("Help")
            about_action = QAction("About", self)
            help_menu.addAction(about_action)

        def tree_view():
            # Create_tree_view
            # Create a dock widget for the tree view
            self.dock_widget = QDockWidget("Simulation Components", self)
            self.addDockWidget(Qt.LeftDockWidgetArea, self.dock_widget)

            # Create the tree view
            self.tree_view = QTreeView()
            self.dock_widget.setWidget(self.tree_view)

            # Set up a standard item model
            self.model = QStandardItemModel()
            self.model.setHorizontalHeaderLabels(["Components"])
            self.tree_view.setModel(self.model)

            # Add a root item
            self.root_item = QStandardItem("Model")
            self.model.appendRow(self.root_item)

            # Add a root writer item
            self.writer_item = Writer("Writer")
            self.root_item.appendRow(self.writer_item)

            # Connect double-click signal
            self.tree_view.doubleClicked.connect(self.double_click_on_writer)

            # Set up context menu
            self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree_view.customContextMenuRequested.connect(self.open_context_menu)

        def main_window():
            # Set up the main window
            self.setWindowTitle("yapfc")
            self.setGeometry(100, 100, 800, 600)

            # Create the central widget
            self.central_widget = vtkViewer()
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)

            # Create the status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)

            # Create_menus
            self.menu_bar = self.menuBar()

        main_window()
        file_menu()
        edit_menu()
        view_menu()
        tools_menu()
        help_menu()
        tree_view()

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;STL Files (*.stl)", options=options)
        return file_name

    def double_click_on_writer(self, index):
        item = self.model.itemFromIndex(index)
        if isinstance(item, Writer):
            item.doubleClicked()

    def open_context_menu(self, position: QPoint):
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            selected_item = self.model.itemFromIndex(indexes[0])
        else:
            selected_item = self.root_item

        menu = QMenu()
        add_item = QAction("Add Item", self)
        remove_item = QAction("Remove Item", self)
        add_step = QAction("Add Step", self)
        remove_step = QAction("Remove Step", self)
        menu.addAction(add_item)
        menu.addAction(add_step)
        # Only add the remove action if the selected item is not the root item
        if isinstance(selected_item, Writer) and not (isinstance(selected_item, Step)):
            menu.addAction(remove_item)
        if isinstance(selected_item, Step):
            menu.addAction(remove_step)

        add_item.triggered.connect(lambda: self.add_item(selected_item))
        remove_item.triggered.connect(lambda: self.remove_item(selected_item))

        add_step.triggered.connect(lambda: self.add_step(selected_item))
        remove_step.triggered.connect(lambda: self.remove_step(selected_item))

        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def add_item(self, parent_item):
        text, ok = QInputDialog.getText(self, "Add Item", "Enter item name:")
        if ok and text:
            new_item = Writer(text)
            parent_item.appendRow(new_item)

    def remove_item(self, item):
        if item.parent():
            item.parent().removeRow(item.row())
        else:
            self.model.removeRow(item.row())

    def add_step(self, parent_item):
        text, ok = QInputDialog.getText(self, "Add Step", "Enter Step name:")
        if ok and text:
            new_item = Step(text)
            parent_item.appendRow(new_item)

    def remove_step(self, item):
        if item.parent():
            item.parent().removeRow(item.row())
        else:
            self.model.removeRow(item.row())
