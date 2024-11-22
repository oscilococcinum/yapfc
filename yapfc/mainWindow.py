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
from .model import Writer, Step
from .mesh import Mesh


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.mesh = None

        def file_menu(self):
            # File menu
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
            # Edit menu
            self.edit_menu = self.menu_bar.addMenu("Edit")
            self.undo_action = QAction("Undo", self)
            self.redo_action = QAction("Redo", self)
            self.edit_menu.addAction(self.undo_action)
            self.edit_menu.addAction(self.redo_action)

        def view_menu(self):
            # View menu
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
            # Tools menu
            self.tools_menu = self.menu_bar.addMenu("Tools")
            # Add tools actions here

        def help_menu(self):
            # Help menu
            self.help_menu = self.menu_bar.addMenu("Help")
            self.about_action = QAction("About", self)
            self.help_menu.addAction(self.about_action)

        def tree_view(self):
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

        def main_window(self):
            # Set up the main window
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

    def open_mesh(self):
        fpath = self.open_file_dialog()
        self.mesh = Mesh(fpath)
        return self.mesh.actor

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
