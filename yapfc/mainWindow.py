from PySide6.QtWidgets import (
    QMainWindow,
    QStatusBar,
    QVBoxLayout,
    QDockWidget,
    QTreeView,
    QMenu,
    QInputDialog,
    QFileDialog
)
from PySide6.QtGui import (
    QAction,
    QStandardItemModel,
    QStandardItem
)
from PySide6.QtCore import Qt, QPoint
from .viewer import vtkViewer
from .model import (
    CcxWriter, MeshSubWriter, MaterialSubWriter,
    SectionSubWriter, ConstraintSubWriter, ContactSubWriter,
    AmplitudeSubWriter, InitialConditionSubWriter, StepSubWriter,
    Label, AnalysisSubWriter, BoundarySubWriter
)
from .mesh import Mesh


def list_children(item):
    children = []
    for row in range(item.rowCount()):
        child = item.child(row)
        children.append(child)
        children.extend(list_children(child))
    return children

def list_model_children(model):
    children = []
    for row in range(model.rowCount()):
        item = model.item(row)
        children.append(item)
        children.extend(list_children(item))
    return children

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.components: list[any] = []
        self.mesh = None

        def file_menu(self):
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

        def edit_menu(self):
            self.edit_menu = self.menu_bar.addMenu("Edit")
            self.undo_action = QAction("Undo", self)
            self.redo_action = QAction("Redo", self)
            self.edit_menu.addAction(self.undo_action)
            self.edit_menu.addAction(self.redo_action)

        def view_menu(self):
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

        def tools_menu(self):
            self.tools_menu = self.menu_bar.addMenu("Tools")

        def help_menu(self):
            self.help_menu = self.menu_bar.addMenu("Help")
            self.about_action = QAction("About", self)
            self.help_menu.addAction(self.about_action)

        def tree_view(self):
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
            self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
            self.tree_view.customContextMenuRequested.connect(self.open_context_menu)

        def main_window(self):
            self.setWindowTitle("yapfc")
            self.setGeometry(100, 100, 800, 600)

            # Create the central widget
            self.central_widget = vtkViewer(self.mesh)
            self.setCentralWidget(self.central_widget)
            self.layout = QVBoxLayout(self.central_widget)

            # Create the status bar
            self.status_bar = QStatusBar()
            self.setStatusBar(self.status_bar)

            # Create_menus
            self.menu_bar = self.menuBar()

        main_window(self)
        file_menu(self)
        edit_menu(self)
        view_menu(self)
        tools_menu(self)
        help_menu(self)
        tree_view(self)

    def open_file_dialog(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Open File", "", "All Files (*);;STL Files (*.stl);;Mesh Files (*.mesh);;Msh Files (*.msh)", options=options)
        return file_name

    def double_click_on_writer(self, index):
        item = self.model.itemFromIndex(index)
        if isinstance(item, CcxWriter):
            item.doubleClicked()

    def open_context_menu(self, position: QPoint):
        indexes = self.tree_view.selectedIndexes()
        if indexes:
            selected_item = self.model.itemFromIndex(indexes[0])
        else:
            selected_item = self.root_item

        menu = QMenu()
        addItem = QAction("Add Item", self)
        addBoundary = QAction("Add Boundary", self)
        removeItem = QAction("Remove Item", self)
        runAnalysis = QAction("Run Analysis", self)

        match selected_item.getTextLabel():
            case "Meshes":
                menu.addAction(addItem)
            case "Materials":
                menu.addAction(addItem)
            case "Sections":
                menu.addAction(addItem)
            case "Contacts":
                menu.addAction(addItem)
            case "Initial Conditions":
                menu.addAction(addItem)
            case "Steps":
                menu.addAction(addItem)
            case "Analyses":
                menu.addAction(addItem)

            case "Mesh":
                menu.addAction(removeItem)
            case "Material":
                menu.addAction(removeItem)
            case "Section":
                menu.addAction(removeItem)
            case "Contact":
                menu.addAction(removeItem)
            case "Initial Condition":
                menu.addAction(removeItem)
            case "Step":
                 menu.addAction(removeItem)
                 menu.addAction(addBoundary)
            case "Analysis":
                menu.addAction(removeItem)
                menu.addAction(runAnalysis)

        addItem.triggered.connect(lambda: self.addItem(selected_item))
        addBoundary.triggered.connect(lambda: self.addBoundary(selected_item))
        removeItem.triggered.connect(lambda: self.removeItem(selected_item))
        runAnalysis.triggered.connect(lambda: self.runAnalysis())

        menu.exec(self.tree_view.viewport().mapToGlobal(position))

    def open_mesh(self):
        fpath = self.open_file_dialog()
        self.mesh = Mesh(fpath)
        return self.mesh.actor

    def addItem(self, parent_item):
        if parent_item.hasChildren(): nextIndex: int = parent_item.rowCount()
        else: nextIndex: int = 0
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

            parent_item.appendRow(new_item)
            if not isinstance(new_item, AnalysisSubWriter):
                self.components.append(new_item)

    def addBoundary(self, parent_item: QStandardItem):
        if parent_item.hasChildren(): nextIndex: int = parent_item.rowCount()
        else: nextIndex: int = 0
        text, ok = QInputDialog.getText(self, "Add Boundary", "Enter item name:", text=f"Boundary{nextIndex}")
        if ok and text:
            new_item = BoundarySubWriter(text)
            parent_item.appendRow(new_item)

    def removeItem(self, item):
        if item.parent():
            item.parent().removeRow(item.row())
            self.components.remove(item)
        else:
            self.model.removeRow(item.row())
            self.components.remove(item)

    def runAnalysis(self):
        comp: CcxWriter
        for comp in self.components:
            print(comp.get_text())