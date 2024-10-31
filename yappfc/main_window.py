from PySide6.QtWidgets import QApplication, QMainWindow, QToolBar, QStatusBar, QWidget, QVBoxLayout, QDockWidget, QTreeView, QMenu, QInputDialog
from PySide6.QtGui import QAction, QStandardItemModel, QStandardItem
from PySide6.QtCore import Qt, QPoint
from .ccx_tools import Writer, step, nodes, elements


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set up the main window
        self.setWindowTitle("yapfc")
        self.setGeometry(100, 100, 800, 600)

        # Create the menu bar
        self.create_menus()

        # Create the toolbars
        self.create_toolbar()

        # Create the central widget
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.layout = QVBoxLayout(self.central_widget)

        # Create the status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        # Create the tree view for simulation components
        self.create_tree_view()

    def create_menus(self):
        self.menu_bar = self.menuBar()

        # File menu
        file_menu = self.menu_bar.addMenu("File")
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(open_action)
        file_menu.addAction(save_action)
        file_menu.addAction(exit_action)

        # Edit menu
        edit_menu = self.menu_bar.addMenu("Edit")
        undo_action = QAction("Undo", self)
        redo_action = QAction("Redo", self)
        edit_menu.addAction(undo_action)
        edit_menu.addAction(redo_action)

        # View menu
        view_menu = self.menu_bar.addMenu("View")
        # Add view actions here

        # Tools menu
        tools_menu = self.menu_bar.addMenu("Tools")
        # Add tools actions here

        # Help menu
        help_menu = self.menu_bar.addMenu("Help")
        about_action = QAction("About", self)
        help_menu.addAction(about_action)

    def create_toolbar(self):
        self.tool_bar = QToolBar("Main Toolbar")
        self.addToolBar(self.tool_bar)

        # Add actions to the toolbar
        open_action = QAction("Open", self)
        save_action = QAction("Save", self)
        self.tool_bar.addAction(open_action)
        self.tool_bar.addAction(save_action)

    def create_tree_view(self):
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

        # Add a writer item
        self.writer_item = Writer("Writer")
        self.root_item.appendRow(self.writer_item)

        # Connect double-click signal
        self.tree_view.doubleClicked.connect(self.on_double_click)

        # Set up context menu
        self.tree_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self.tree_view.customContextMenuRequested.connect(self.open_context_menu)

    def on_double_click(self, index):
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
        add_step = QAction("Add step", self)
        remove_step = QAction("Remove step", self)
        menu.addAction(add_item)
        menu.addAction(add_step)
        # Only add the remove action if the selected item is not the root item
        if isinstance(selected_item, Writer) and not (isinstance(selected_item, step)):
            menu.addAction(remove_item)
        if isinstance(selected_item, step):
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
            new_item = step(text)
            parent_item.appendRow(new_item)

    def remove_step(self, item):
        if item.parent():
            item.parent().removeRow(item.row())
        else:
            self.model.removeRow(item.row())

